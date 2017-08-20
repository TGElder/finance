def test_get_accounts(get_finance):
    accounts = get_finance.get_accounts()
    
    assert(accounts[0] == "Car")
    assert(accounts[1] == "Joint")
    assert(accounts[2] == "Long Term Savings")
    assert(accounts[3] == "Outside")
    assert(accounts[4] == "Personal")
    assert(accounts[5] == "Savings")
    assert(accounts[6] == "Short Term Savings")

def test_get_next_transaction_id(get_finance):
    assert(get_finance.get_next("_id","transactions")==7)

def test_get_next_commitment_id(get_finance):
    assert(get_finance.get_next("_id","commitments")==4)    
    
def test_get_next_reading_id(get_finance):
    assert(get_finance.get_next("_id","readings")==13)
    
def test_get_latest_reading(get_finance):
    assert(get_finance.get_latest_reading("Personal")==90009)
    assert(get_finance.get_latest_reading("Savings")==900009)
    assert(get_finance.get_latest_reading("Joint")==40004)
    
def test_get_credit(get_finance):
    assert(get_finance.get_credit("Car")==10993)
    assert(get_finance.get_credit("Joint")==-14997)
    assert(get_finance.get_credit("Long Term Savings")==300003)    
    assert(get_finance.get_credit("Outside")==0)    
    assert(get_finance.get_credit("Personal")==34007)    
    assert(get_finance.get_credit("Savings")==-400004)    
    assert(get_finance.get_credit("Short Term Savings")==69998)

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
    
def test_set_closed_credit_to_zero(get_finance):
    balanceBefore = get_finance.get_total_balance()
    
    get_finance.set_closed_credit_to_zero("Personal","Savings")
    
    assert(get_finance.get_total_balance()==balanceBefore)
    assert(get_finance.get_credit("Personal")==0)
        
    get_finance.set_closed_credit_to_zero("Joint","Savings")
    
    assert(get_finance.get_total_balance()==balanceBefore)
    assert(get_finance.get_credit("Joint")==0)
   
    get_finance.load()
    
def test_insert_transaction(get_finance):
    
    next = get_finance.get_next("_id","transactions")

    get_finance.insert_transaction("Short Term Savings","Personal","Lens",444.44)
    
    get_finance.get_cursor().execute("""
    select _from,_to,_what,_amount,_added
    from transactions
    where _id = ?
    """, (next,))
    
    results = get_finance.get_cursor().fetchone()
    
    assert(results[0]=="Short Term Savings")
    assert(results[1]=="Personal")
    assert(results[2]=="Lens")
    assert(results[3]=="444.44")
    assert(results[4]==get_finance.get_timestamp())
    
    