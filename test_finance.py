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
    assert(get_finance.get_next("_id","transactions")==9)

def test_get_next_reading_id(get_finance):
    assert(get_finance.get_next("_id","readings")==13)
    
def test_get_latest_reading(get_finance):
    assert(get_finance.get_latest_reading("Personal")==90009)
    assert(get_finance.get_latest_reading("Savings")==900009)
    assert(get_finance.get_latest_reading("Joint")==40004)
    
def test_get_credit(get_finance):
    assert(get_finance.get_credit("Car",False)==10993)
    assert(get_finance.get_credit("Joint",False)==-14997)
    assert(get_finance.get_credit("Long Term Savings",False)==300003)    
    assert(get_finance.get_credit("Outside",False)==391996)    
    assert(get_finance.get_credit("Personal",False)==42015)    
    assert(get_finance.get_credit("Savings",False)==-800008)    
    assert(get_finance.get_credit("Short Term Savings",False)==69998)
    
def test_get_credit_closed(get_finance):
    assert(get_finance.get_credit("Car",True)==10993)
    assert(get_finance.get_credit("Joint",True)==-14997)
    assert(get_finance.get_credit("Long Term Savings",True)==300003)    
    assert(get_finance.get_credit("Outside",True)==0)    
    assert(get_finance.get_credit("Personal",True)==34007)    
    assert(get_finance.get_credit("Savings",True)==-400004)    
    assert(get_finance.get_credit("Short Term Savings",True)==69998)
    
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
    assert(get_finance.get_credit("Personal",True)==0)
        
    get_finance.set_closed_credit_to_zero("Joint","Savings")
    
    assert(get_finance.get_total_balance()==balanceBefore)
    assert(get_finance.get_credit("Joint",True)==0)