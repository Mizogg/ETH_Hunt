# -*- coding: utf-8 -*-
from web3 import Web3
import random, time
import secp256k1 as ice
from multiprocessing import Event, Process, Queue, Value, cpu_count

mylist=[]
with open('api.txt', newline='', encoding='utf-8') as f:
    for line in f:
        mylist.append(line.strip())
api = random.choice(mylist)
def get_balance(this_eth):

    zmok_url=('https://api.zmok.io/mainnet/' + api)
    zmok_w3 = Web3(Web3.HTTPProvider(zmok_url))
    Zmok_check_sum = zmok_w3.toChecksumAddress(this_eth)
    Zmok = zmok_w3.eth.get_balance(Zmok_check_sum)
    balance = Zmok
    return balance
    
def hunt_ETH_address(cores='all'):

    try:
        available_cores = cpu_count()
    
        if cores == 'all':
            cores = available_cores
        elif 0 < int(cores) <= available_cores:
            cores = int(cores)
        else:
            cores = 1
    
        counter = Value('L')
        match = Event()
        queue = Queue()
    
        workers = []
        for r in range(cores):
            p = Process(target=generate_key_address_pairs, args=(counter, match, queue, r, start, group_size))
            workers.append(p)
            p.start()
    
        for worker in workers:
            worker.join()
    
    except(KeyboardInterrupt, SystemExit):
        exit('\nSIGINT or CTRL-C detected. Exiting gracefully. BYE')

    
    private_key, address = queue.get()
    print('\n\nPrivate Key(dec):', private_key, '\nPrivate Key(hex):', hex(private_key), '\nETH Address : ', address, '  Balance = ', get_balance(address))
    with open("winner.txt", "a") as f:
        f.write(f"""\nPrivate Key In DEC :  {private_key}
Privatekey in HEX  : {hex(private_key)}
Public Address ETH:  {address}  Balance = {get_balance(address)}""")

def generate_key_address_pairs(counter, match, queue, r, start, group_size):
    st = time.time()

    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    key_int = random.SystemRandom().randint(start,N)

    P = ice.scalar_multiplication(key_int)
    current_pvk = key_int + 1
    
    print('Starting thread:', r, 'base: ',hex(key_int))

    while True:
        try:
            if match.is_set():
                return
    
            with counter.get_lock():
                counter.value += group_size
    
            
            Pv = ice.point_sequential_increment(group_size, P)
    
            for t in range(group_size):
                this_eth = ice.pubkey_to_ETH_address(Pv[t*65:t*65+65])
                balance = get_balance(this_eth)
                if balance > 0:
                    match.set()
                    queue.put_nowait((current_pvk+t, this_eth))
                    return
            
            if (counter.value)%group_size == 0:
                print('[+] Total Keys Checked : {0}  [ Speed : {1:.2f} Keys/s ]  Current ETH: {2}'.format(counter.value, counter.value/(time.time() - st), this_eth), ' Balance ', get_balance(this_eth))
    
            
            P = Pv[-65:]
            current_pvk += group_size
        
        except(KeyboardInterrupt, SystemExit):
            break

if __name__ == '__main__':
    start=int(input("start range Min 1-115792089237316195423570985008687907852837564279074904382605163141518161494335 -> "))
    cpucores=int(input("Ammount of Cores Multi Process 1 - 16 (8 works best with 1 Group and 1 API) "))
    group_size=int(input("Group Size from Privatekey "))   
    print('[+] Starting.........Wait.....')
    hunt_ETH_address(cores = cpucores)
