def test_get_accounts(get_finance):
    accounts = get_finance.get_accounts()
    
    assert(accounts[0] == "Car")
    assert(accounts[1] == "Joint")
    assert(accounts[2] == "Long Term Savings")
    assert(accounts[3] == "Outside")
    assert(accounts[4] == "Personal")
    assert(accounts[5] == "Savings")
    assert(accounts[6] == "Short Term Savings")

def test_get_next_transfer_id(get_finance):
    assert(get_finance.get_next("_id","transfers")==7)

def test_get_next_commitment_id(get_finance):
    assert(get_finance.get_next("_id","commitments")==4)    
    
def test_get_next_reading_id(get_finance):
    assert(get_finance.get_next("_id","readings")==13)
    
def test_get_latest_reading(get_finance):
    assert(get_finance.get_latest_reading("Personal")==90009)
    assert(get_finance.get_latest_reading("Savings")==900009)
    assert(get_finance.get_latest_reading("Joint")==40004)
    
def test_get_transfer(get_finance):
    assert(get_finance.get_transfer("Car")==10993)
    assert(get_finance.get_transfer("Joint")==-14997)
    assert(get_finance.get_transfer("Long Term Savings")==300003)    
    assert(get_finance.get_transfer("Outside")==0)    
    assert(get_finance.get_transfer("Personal")==34007)    
    assert(get_finance.get_transfer("Savings")==-400004)    
    assert(get_finance.get_transfer("Short Term Savings")==69998)

def test_get_commitment(get_finance):
    assert(get_finance.get_commitment("Car")==0)
    assert(get_finance.get_commitment("Joint")==-0)
    assert(get_finance.get_commitment("Long Term Savings")==0)    
    assert(get_finance.get_commitment("Outside")==391996)    
    assert(get_finance.get_commitment("Personal")==8008)    
    assert(get_finance.get_commitment("Savings")==-400004)    
    assert(get_finance.get_commitment("Short Term Savings")==0)  
    
def test_get_balance(get_finance):
    assert(get_finance.get_balance("Car")==10993)
    assert(get_finance.get_balance("Joint")==25007)
    assert(get_finance.get_balance("Long Term Savings")==300003)    
    assert(get_finance.get_balance("Outside")==391996)    
    assert(get_finance.get_balance("Personal")==132024)    
    assert(get_finance.get_balance("Savings")==100001)    
    assert(get_finance.get_balance("Short Term Savings")==69998)
    
def test_get_total_balance(get_finance):
    assert(get_finance.get_total_balance()==1030022)
    
def test_set_transfer_to_zero(get_finance):
    totalBalanceBefore = get_finance.get_total_balance()
    savings_balance_before = get_finance.get_balance("Savings")

    personal_balance_before = get_finance.get_balance("Personal")
    
    get_finance.set_transfer_to_zero("Personal","Savings")

    assert(get_finance.get_total_balance()==totalBalanceBefore)
    assert(get_finance.get_balance("Personal")==personal_balance_before)
    assert(get_finance.get_balance("Savings")==savings_balance_before)
    assert(get_finance.get_transfer("Personal")==0)
    
    joint_balance_before = get_finance.get_balance("Joint")
    
    get_finance.set_transfer_to_zero("Joint","Savings")
    
    assert(get_finance.get_total_balance()==totalBalanceBefore)
    assert(get_finance.get_balance("Joint")==joint_balance_before)
    assert(get_finance.get_balance("Savings")==savings_balance_before)
    assert(get_finance.get_transfer("Joint")==0)
   
def test_insert_transfer(get_finance):
    
    next = get_finance.get_next("_id","transfers")

    get_finance.insert_transfer("Short Term Savings","Personal","Lens",44444)
    
    get_finance.get_cursor().execute("""
    select _from,_to,_what,_amount,_added
    from transfers
    where _id = ?
    """, (next,))
    
    results = get_finance.get_cursor().fetchone()
    
    assert(results[0]=="Short Term Savings")
    assert(results[1]=="Personal")
    assert(results[2]=="Lens")
    assert(results[3]=="44444")
    assert(results[4]==get_finance.get_timestamp())
        
def test_insert_commitment(get_finance):
    next = get_finance.get_next("_id","commitments")

    get_finance.insert_commitment("Personal","Outside","Holiday Balance",11111)
    
    get_finance.get_cursor().execute("""
    select _from,_to,_what,_amount,_added
    from commitments
    where _id = ?
    """, (next,))
    
    results = get_finance.get_cursor().fetchone()
    
    assert(results[0]=="Personal")
    assert(results[1]=="Outside")
    assert(results[2]=="Holiday Balance")
    assert(results[3]=="11111")
    assert(results[4]==get_finance.get_timestamp())

def test_close_commitment(get_finance):
    get_finance.close_commitment(2)
    get_finance.close_commitment(3)
    assert(get_finance.get_commitment("Outside")==0)    
    assert(get_finance.get_commitment("Personal")==0)    
    assert(get_finance.get_commitment("Savings")==-0) 
    
def test_insert_reading(get_finance):
    get_finance.insert_reading("Savings",950059)
    
    assert(get_finance.get_latest_reading("Savings")==950059)
    
def test_create_transfers_from_table(get_finance):
    next = get_finance.get_next("_id","transfers")

    get_finance.create_transfers_from_table("monthly_budget","August")

    get_finance.get_cursor().execute("""
    select _from,_to,_what,_amount,_added
    from transfers
    where _id = ?
    """, (next,))
    
    results = get_finance.get_cursor().fetchone()
    
    assert(results[0]=="Savings")
    assert(results[1]=="Short Term Savings")
    assert(results[2]=="August Monthly")
    assert(results[3]=="25025")
    assert(results[4]==get_finance.get_timestamp())

    get_finance.get_cursor().execute("""
    select _from,_to,_what,_amount,_added
    from transfers
    where _id = ?
    """, (next + 1,))
    
    results = get_finance.get_cursor().fetchone()
    
    assert(results[0]=="Savings")
    assert(results[1]=="Long Term Savings")
    assert(results[2]=="August Monthly")
    assert(results[3]=="35035")
    assert(results[4]==get_finance.get_timestamp())
