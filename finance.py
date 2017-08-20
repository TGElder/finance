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

    def get_accounts(self):
            self.tb.cursor.execute("""
            select distinct account from
            (
                select distinct _from as account
                from transactions
                
                union
                
                select distinct _to as account
                from transactions
                
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
    
    def get_credit(self,account, closed_only):
        
        if closed_only:
            closed = 1
        else:
            closed = 0
            
        self.tb.cursor.execute("""
        with credits as
        (
            select round(sum(_amount),2) as credit
            from transactions t
            where ((t._id in (select _transaction_id from close_dates)) or not(?))
            and _to = ?
        ),
        debits as
        (
            select round(sum(_amount),2) as debit
            from transactions t
            where ((t._id in (select _transaction_id from close_dates)) or not(?))
            and _from = ?
        )
        select round(coalesce(credit,0) - coalesce(debit,0),2)
        from credits
        cross join debits
        """, (closed,account,closed,account))
        
        return int(self.tb.cursor.fetchone()[0])

    def get_balance(self,account):
        return self.get_latest_reading(account) + self.get_credit(account, False)
        
    def get_total_balance(self):
        out = 0
        
        for account in self.get_accounts():
            out += self.get_balance(account)
            
        return out
            
        
    def set_closed_credit_to_zero(self,account,using):
        amount = self.get_credit(account,True)
        
        from_account = None
        to_account = None
        if amount > 0:
            from_account = account
            to_account = using
        else:
            from_account = using
            to_account = account
            
        self.insertTransaction(from_account,
                               to_account,
                               "Zeroing Transfer",
                               abs(amount),
                               True)
    
        reading = self.get_latest_reading(account)
        self.insertReading(account,reading+amount)
        
        reading = self.get_latest_reading(using)        
        self.insertReading(using,reading-amount)

        print("Transfer "+str(abs(amount))+" from "+to_account+" to "+from_account+"!")
        
    
    def insertTransaction(self,from_account, to_account, what, amount, closed):
        
        id = self.get_next("_id","transactions")
        
        self.tb.cursor.execute(
        "insert into transactions values(?, ?, ?, ?, ?, ?)",
        (id,
        from_account,
        to_account,
        what,
        str(amount),
        self.getTimestamp()))
    
        if closed:    
            self.closeTransaction(id)
            
    def closeTransaction(self,id):
        self.tb.cursor.execute(
        "insert into close_dates values(?, ?)",
        (id,
        self.getTimestamp()))
        
    def insertReading(self,account,reading):
        self.tb.cursor.execute(
        "insert into readings values(?, ?, ?, ?)",
        (self.get_next("_id","readings"),
        account,
        str(reading),
        self.getTimestamp()))
        

        

    
    def getTimestamp(self):
        return datetime.now().strftime("%d-%m-%y")
        
    def insertMonthlys(self,version, month):
        self.tb.cursor.execute("""
        select _from,_to,_what,_amount
        from monthly_budget
        where _version = ?
        """, (version,))
        
        for row in self.tb.cursor.fetchall():
            self.insertTransaction(row[0],
                              row[1],
                              month+" "+row[2], 
                              row[3], 
                              True)
        
        
    def printSummary(self):
        print("Account".ljust(16)
        +"Last Reading +".ljust(16)
        +"Credit =".ljust(16)
        +"Balance".ljust(16)
        +"Credit (Closed)".ljust(16)
        )
        for account in self.get_accounts():
            print(account.ljust(16)
            +str(self.get_latest_reading(account)).ljust(16)
            +str(self.get_credit(account, False)).ljust(16)
            +str(self.get_balance(account)).ljust(16)
            +str(self.get_credit(account, True)).ljust(16)
            )