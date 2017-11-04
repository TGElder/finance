from textbase import Textbase
from datetime import datetime


class Finance:
    
    tb = None
    
    def __init__(self, database):
        self.tb = Textbase(database)
        self.tb.load()
        
    def load(self):
        self.tb.load()
        
    def save(self):
        self.tb.save()
        
    def get_cursor(self):
        return self.tb.cursor

    def get_accounts(self):
            self.tb.cursor.execute("""
            select distinct account from
            (
                select distinct _from as account
                from transfers
                
                union
                
                select distinct _to as account
                from transfers
                
                union
                
                select distinct _from as account
                from commitments
                
                union
                
                select distinct _to as account
                from commitments
                
                union
                
                select distinct _account as account
                from readings
            )
            order by account
            """)
            
            out = []
            
            for row in self.tb.cursor.fetchall():
                out.append(row[0])
                
            return out
        
    def get_next(self,field,table):
        self.tb.cursor.execute("""
        select max(cast({} as int))
        from {}
        """.format(field,table))
        
        return int(self.tb.cursor.fetchone()[0]) + 1
        
    def get_latest_reading(self,account):
        self.tb.cursor.execute("""
        with max_id as
        (
            select cast(max(cast(_id as int)) as string) as max_id
            from readings
            where _account = ?
            group by _account
        )
        select r._reading
        from readings r
        inner join max_id m
        on r._id = m.max_id
        """, (account,))
        
        out = self.tb.cursor.fetchone()
        
        if out:
            return int(out[0])
        else:
            return 0    
    
    def get_transfer(self,account):
        
        self.tb.cursor.execute("""
        with credits as
        (
            select sum(_amount) as credit
            from transfers t
            where _to = ?
        ),
        debits as
        (
            select sum(_amount) as debit
            from transfers t
            where _from = ?            
        )
        select coalesce(credit,0) - coalesce(debit,0)
        from credits
        cross join debits
        """, (account,account))
        
        return int(self.tb.cursor.fetchone()[0])

    def get_commitment(self,account):

        self.tb.cursor.execute("""
        with credits as
        (
            select sum(_amount) as credit
            from commitments c
            where (c._id not in (select _commitment_id from close_dates))
            and _to = ?
        ),
        debits as
        (
            select sum(_amount) as debit
            from commitments c
            where (c._id not in (select _commitment_id from close_dates))
            and _from = ?
        )
        select coalesce(credit,0) - coalesce(debit,0)
        from credits
        cross join debits
        """, (account,account))
        
        return int(self.tb.cursor.fetchone()[0])        
        
    def get_balance(self,account):
        return self.get_latest_reading(account) + self.get_transfer(account) + self.get_commitment(account)
        
    def get_total_balance(self):
        out = 0
        
        for account in self.get_accounts():
            out += self.get_balance(account)
            
        return out
      
    def get_timestamp(self):
        return datetime.now().strftime("%d-%m-%y")      

    def _insert(self, table, from_account, to_account, what, amount):
        id = self.get_next("_id",table)
        
        self.tb.cursor.execute(
        "insert into {} values(?, ?, ?, ?, ?, ?)".format(table),
        (id,
        from_account,
        to_account,
        what,
        str(amount),
        self.get_timestamp()))
        
    def insert_transfer(self,from_account, to_account, what, amount):
        self._insert("transfers", from_account, to_account, what, amount)
  
    def insert_commitment(self,from_account, to_account, what, amount):
        self._insert("commitments", from_account, to_account, what, amount)

    def close_commitment(self,id):
        self.tb.cursor.execute(
        "insert into close_dates values(?, ?)",
        (id,
        self.get_timestamp()))        
        
    def insert_reading(self,account,reading):
        self.tb.cursor.execute(
        "insert into readings values(?, ?, ?, ?)",
        (self.get_next("_id","readings"),
        account,
        str(reading),
        self.get_timestamp()))
        
    def set_transfer_to_zero(self,account,using):
        amount = self.get_transfer(account)
        
        from_account = None
        to_account = None
        if amount > 0:
            from_account = account
            to_account = using
        else:
            from_account = using
            to_account = account
            
        self.insert_transfer(from_account,
                               to_account,
                               "Zeroing Transfer",
                               abs(amount))
    
        reading = self.get_latest_reading(account)
        self.insert_reading(account,reading+amount)
        
        reading = self.get_latest_reading(using)        
        self.insert_reading(using,reading-amount)

        print("Transfer "+str(abs(amount/100))+" from "+to_account+" to "+from_account+"!")
        
    def create_transfers_from_table(self,table,prefix=""):
        self.tb.cursor.execute("""
        select _from,_to,_what,_amount
        from {}
        """.format(table))
        
        if prefix:
            prefix = prefix+" "
        
        for row in self.tb.cursor.fetchall():
            self.insert_transfer(row[0],
                              row[1],
                              prefix+row[2], 
                              row[3])
        
    def print_summary(self):
        print("Account".ljust(16)
        +"Last Reading +".ljust(16)
        +"Transfer +".ljust(16)
        +"Commitment =".ljust(16)
        +"Balance".ljust(16))
        
        for account in self.get_accounts():
            print(account.ljust(16)
            +str(self.get_latest_reading(account)/100).ljust(16)
            +str(self.get_transfer(account)/100).ljust(16)
            +str(self.get_commitment(account)/100).ljust(16)
            +str(self.get_balance(account)/100).ljust(16))
