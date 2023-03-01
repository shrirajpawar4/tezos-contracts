import time
import smartpy as sp

class Crowdfund(sp.Contract):
    def __init__(self, owner, amount, maxTime):
        self.init(
            funding = sp.map(tkey = sp.TAddress, tvalue = None),
            owner = owner,
            amount = amount,
            maxTime = maxTime
        )
        
    @sp.entry_point
    def send(self):
        sp.verify(self.data.maxTime >= sp.now)
        sp.verify(~self.data.funding.contains(sp.sender))
        self.data.funding[sp.sender] = sp.amount

    @sp.entry_point
    def pay_owner(self):
        sp.verify(self.data.owner == sp.sender)
        sp.verify(self.data.amount <= sp.balance)
        sp.verify(self.data.maxTime <= sp.now)
        sp.send(self.data.owner, sp.balance)

    @sp.entry_point
    def refund(self):
        sp.verify(self.data.funding.contains(sp.sender))
        sp.verify(self.data.maxTime < sp.now)
        sp.verify(self.data.amount > sp.balance)
        sp.send(sp.sender, self.data.funding[sp.sender])
        del self.data.funding[sp.sender]

@sp.add_test(name = 'Funding done')
def success():
    owner= sp.address("tz1xowner")
    user1= sp.address("tz1xuser1")
    user2= sp.address("tz1xuser2")
    user3= sp.address("tz1xuser3")

    #amount = 20
    #deadline = 3d

    contract = Crowdfund(owner, sp.tez(20), sp.timestamp(int(time.time())+259200))
    
    scenario = sp.test_scenario()
    scenario += contract

    scenario += contract.send().run(sender=user1, amount=sp.tez(10), now = sp.timestamp(int(time.time())+100))
    scenario += contract.send().run(sender=user2, amount=sp.tez(8), now = sp.timestamp(int(time.time())+200))

    #should fail as user1 cant fund/vote again. implement this for vote as well
    scenario += contract.send().run(sender=user1, amount=sp.tez(12), now = sp.timestamp(int(time.time())+300), valid = False)

    #missing amount.
    scenario += contract.pay_owner().run(sender=owner, 
    now = sp.timestamp(int(time.time())+300), valid = False)

    #user3 donate
    scenario += contract.send().run(sender=user3, amount=sp.tez(15), now = sp.timestamp(int(time.time())+400))


    #should fail because can't payout before deadline
    scenario += contract.pay_owner().run(sender=owner, 
    now = sp.timestamp(int(time.time())+500), valid = False)

    scenario += contract.pay_owner().run(sender=owner, 
    now = sp.timestamp(int(time.time())+259200))

    

    
    
        
        
