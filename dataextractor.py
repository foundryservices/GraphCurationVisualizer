import pickle
import os.path
import re
from os import path
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


DRIVER_PATH = './chromedriver'

base_url = "https://rinkeby.etherscan.io"
token_path = "/token/"

class Transaction:
    def __init__(self, date, cur_address, tok_address, ttype, grt, gst, burned=0):
        """
        Parameters
        ----------
        date : datetime 
            time of transaction
        cur_address: string
            address of transaction origin i.e the curator
        tok_address: string
            address of token
        ttype : string
            transaction type i.e. buy or sell
        grt : float
            quantity of GRT transacted
        gst : float
            quantity of GST transacted
        burned : Float
            quantity of GRT burned on a sale
        """
        self.date = date
        self.cur_address = cur_address
        self.tok_address = tok_address
        self.ttype = ttype
        self.grt = float(grt)
        self.gst = float(gst)
        self.burned = float(burned)


def get_txn_list(addr, one=False, index=0, url=base_url, sub=token_path):
    """
    Parameters
    ----------
    url : string
        base url address
    sub : string
        url subaddress
    addr : string
        contract address for subgraph
    one: bool
        boolean representing if the entire list
        should be returned or only one element
    index: int
        the index of the element being returned if
        one element is being returned
    Returns
    -------
    list
        list of transactions url endings
    """
    all_txn = []
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    driver.get(url + sub + addr)
    driver.switch_to.frame('tokentxnsiframe')
    if not one:
        pages_done = True
        while pages_done:  # while not on last page
            pages = driver.find_elements_by_tag_name("strong")[0:2]  # pages listed twice, only need the top 2
            pages_done = int(pages[0].text) != int(pages[1].text)  # bool if current page is last page
            txns = BeautifulSoup(driver.page_source, 'html.parser').find_all(href=re.compile("/tx/"))
            all_txn += [tx.attrs['href'] for tx in txns]  # pulls href link out of html tag
            try:
                driver.find_element(By.LINK_TEXT, "Next").click()
            except NoSuchElementException:
                pass
    else:
        txns = BeautifulSoup(driver.page_source, 'html.parser').find_all(href=re.compile("/tx/"))
        if index < len(txns):
            all_txn += [txns[index].attrs['href']]  # pulls href link out of html tag

    driver.quit()
    return all_txn


def get_txn_values(addr, txns, url=base_url):
    """
    Parameters
    ----------
    url : string
        base url address
    addr : string
        token address
    txns : list
        list of transactions url endings

    Returns
    -------
    list
        list of transaction objects
    """
    transactions = []
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    for tx in txns:
        driver.get(url + tx)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cur_addr = soup.find(id='addressCopy').text  # grabs curators address
        transact = soup.find(title=re.compile('\\d Token Transfers'))  # finds token transactions
        date = datestr_to_datetime(soup.find(id="clock").parent.get_text())  # gets date and creates datetime
        if transact.attrs['title'] == "4 Token Transfers":  # GST sold for GRT
            ttype = "sell"
            listitems = transact.parent.parent.parent.find_all("li")
            gst = token_to_text(listitems[0])
            burned = token_to_text(listitems[1])
            grt = token_to_text(listitems[2])
            transactions += [Transaction(date, cur_addr, addr, ttype, grt, gst, burned)]
        else:  # GST bought for GRT
            ttype = "buy"
            listitems = transact.parent.parent.parent.find_all("li")
            grt = token_to_text(listitems[0])
            gst = token_to_text(listitems[2])
            transactions += [Transaction(date, cur_addr, addr, ttype, grt, gst)]
    driver.quit()
    return transactions


def isuptodate(addr, txns, url=base_url, sub=token_path):
    """
    Parameters
    ----------
    addr : string
        token address
    txns : list
        list of transactions url endings
    url : string
        base url string
    sub : string
        sub address for url

    Returns
    -------
    bool
        comparison between two dates
    """

    saved_transact = txns
    current_transact = get_txn_values(addr, get_txn_list(addr, True))
    return current_transact[0].date == saved_transact[0].date


def update_transactions(addr, txns, url=base_url, sub=token_path):
    """
    Parameters
    ----------
    addr : string
        token address
    txns : list
        list of transactions url endings
    url : string
        base url string
    sub : string
        sub address for url

    Returns
    -------
    list
        list of updated transaction objects
    """

    saved_transact = txns
    current_transact = get_txn_values(addr, get_txn_list(addr, True))
    new_transact = []
    index = 0

    while current_transact[0].date > saved_transact[0].date:
        index += 1
        current_transact = get_txn_values(addr, get_txn_list(addr, True, index))
        if current_transact[0].date != saved_transact[0].date:
            new_transact += current_transact # adds new transactions most recent to oldest
    return new_transact + txns # returns the newest transactions as the start of the list 


def get_stored_transactions(token):
    """
    Parameters
    ----------
    token : string
        token name

    Returns
    -------
    list
        list of transaction objects
    """
    dirname = os.path.dirname(__file__)
    filename = path.join(dirname, "./Subgraph Data/" + token + ".p")
    return pickle.load(open(filename, 'rb'))


def store_transactions(token, address):
    """
    Parameters
    ----------
    token : string
        token name
    address : string
        token address

    Returns
    -------
    list
        list of transaction objects
    """

    dirname = os.path.dirname(__file__)
    filename = path.join(dirname, token + ".p")
    if path.exists(filename):
        transactions = update_transactions(address, pickle.load(open(filename, 'rb')))
    else:
        transactions = get_txn_values(address, get_txn_list(address))
    pickle.dump(transactions, open(filename, "wb"))
    return transactions
    

def prepared_transactions(transactions, personal=""):
    """
    Parameters
    ----------
    transactions : list
        list of transaction objects
    personal : string
        string of personal wallet address

    Returns
    -------
    dict
        dictionary of parsed data
    """

    prepared = {
        "txn_buy":[],
        "txn_sell":[],
        "your_txn_buy":[],
        "your_txn_sell":[],
        "tokensupply":0,
        "highestsupply":0,
        "reserves":0
    }
    for t in reversed(transactions): # list is reversed since transaction lists are created in chronological order with recent transactions first
        if t.ttype == "buy":
            if t.cur_address == personal.lower():
                prepared["your_txn_buy"] += [prepared["tokensupply"] + (t.gst)]  # averages out token supply at purchase
            else:
                prepared["txn_buy"] += [prepared["tokensupply"] + (t.gst)]
            prepared["tokensupply"] += t.gst
            prepared["reserves"] += t.grt
        if t.ttype == "sell":
            if t.cur_address == personal.lower():
                prepared["your_txn_sell"] += [prepared["tokensupply"] - (t.gst)]
            else:
                prepared["txn_sell"] += [prepared["tokensupply"] - (t.gst)]
            prepared["tokensupply"] -= t.gst
            prepared["reserves"] -= (t.grt + t.burned)
            prepared["highestsupply"] = prepared["tokensupply"] if prepared["tokensupply"] > prepared["highestsupply"] else prepared["highestsupply"]

    return prepared


def token_to_text(s):
    return s.find("div").find_all("span", class_="mr-1")[-1].get_text(strip=True).replace(',', '')


def datestr_to_datetime(d):
    return datetime.strptime(d.replace(' +UTC)\n', '').split('(')[1], '%b-%d-%Y %I:%M:%S %p')
