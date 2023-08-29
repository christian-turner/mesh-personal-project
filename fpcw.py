# -*- coding: utf-8 -*-
import requests , threading , time , json , random
from bs4 import BeautifulSoup as bs
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = '43ad76eef189c860ec20a3712f62e537'
site_key = '6LfEwHQUAAAAACTyJsAICi2Lz2oweGni8QOhV-Yl' 
keyurl = 'https://www.footpatrol.com/'
pid = ['335608']
urls = [
    'https://m.footpatrol.com/product/nike-air-max-deluxe/'+random.choice(pid)+'_footpatrolcom/quickview/stock/' ,
    'https://www.footpatrol.com/product/black-nike-air-max-deluxe/'+random.choice(pid)+'_footpatrolcom/quickview/stock',
    'https://www.footpatrol.com/product/black-nike-air-max-deluxe/'+random.choice(pid)+'_footpatrolcom/quickwish/',
    'https://m.footpatrol.com/product/blue-reebok-club-c-85-cord/'+random.choice(pid)+'_footpatrolcom/quickwish/',
    'https://www.footpatrol.com/product/black-nike-air-max-deluxe/'+random.choice(pid)+'_footpatrolcom/stock',
    'https://m.footpatrol.com/product/black-nike-air-max-deluxe/'+random.choice(pid)+'_footpatrolcom/stock'
        ]
        

headers = {"User-Agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
global queuecookie
queuecookie = ''
class task:
    
    def __init__(self):
        self.req()

    def req(self):
        self.attempt()
            
    def attempt(self):
        global queuecookie
        queue = 0
        while queue < 1:
            with requests.session() as c:
                cookies = {'akavpau_VP1': queuecookie}
                page1 = c.get('https://www.footpatrol.com/myaccount/dashboard/' , headers=headers , cookies=cookies).text
                if 'Find a Store' in page1:
                    queuecookie = c.cookies['akavpau_VP1']
                    print(queuecookie)
                    print('Through queue - Shared queue cookie to all tasks')
                    queue+=1
                    self.captcha(c)
                else:
                    print('In queue')

                
    def captcha(self , c):
        print('Getting captcha...')
        client = AnticaptchaClient(api_key)
        task = NoCaptchaTaskProxylessTask(keyurl, site_key)
        job = client.createTask(task)
        job.join()
        capt = job.get_solution_response()
        print('Captcha recieved')
        self.getsize(c , capt)

    def getsize(self , c , capt):
        global queuecookie
        timer = 0
        while timer < 50:
            url = random.choice(urls)
            print(url)
            page1 = c.get(url , headers=headers).text
            if 'Select Size' in page1:
                self.sizes(c , page1 , capt , url)
            if 'waiting' in page1:
                check = c.get('https://www.footpatrol.com/myaccount/dashboard/' , headers=headers)
                if 'waiting' in check.text:
                    print('Queue up on sizes page retrying - Obtaining new cookie')
                    queuecookie = ''
                    self.attempt()
            else:
                print('No size values found - Retrying')
                time.sleep(1)
                timer +=1
            if timer == 50 :
                print('Captcha expired.... getting new one')
                self.captcha(c)
            
    def sizes(self , c, page1 , capt , url):
        size_list = []
        findsizes = 4
        while findsizes < 12:
            fs1 = str(findsizes)
            if '.0' in fs1:
                fs1 = fs1.strip('.0')
            fs = 'Select Size ' + fs1
            if fs == 'Select Size 1':
                fs = 'Select Size 10'
            if fs in page1:
                size_list.append(fs)
                findsizes += 0.5
            else:
                findsizes +=0.5
            if findsizes == 12:
                self.atc(c , page1 , capt , size_list , url)

                
            
    def atc(self, c , page1 , capt , size_list , url):
        print('Found all sizes!')
        rsizes = random.choice(size_list)
        print('Selected size ' + rsizes)
        if 'quickview' in url:
            soup = bs(page1, 'html.parser')
            get_sizes = soup.find("button", title = rsizes )
            size = get_sizes['data-sku']
        if 'quickwish' in url:
            soup = bs(page1, 'html.parser')
            get_sizes = soup.find("a", title = rsizes )
            size = get_sizes['data-sku']
        else:
            soup = bs(page1, 'html.parser')
            get_sizes = soup.find("button", title = rsizes )
            size = get_sizes['data-sku']
        sizeurl = 'https://www.footpatrol.com/cart/'+size+'/'
        add = c.post(sizeurl , data = '{"customisations":false,"cartPosition":null,"recaptchaResponse":"'+capt+'","quantityToAdd":1}' , headers=headers)
        if 'GBP' in add.text:
            print('Added '+size+' to cart!')
            self.login(c)
        else:
            print('Atc usuccesfull... Trying again')
            print(add.text)
            self.captcha(c)

    def login(self, c):
        file = open("settings.txt","r")
        lines = file.readlines()
        email = lines[3].strip('\n')
        c.get('https://www.footpatrol.com/checkout/login/', headers=headers)
        c.post(url = 'https://www.footpatrol.com/checkout/guest/'  , data = '{"email": "'+email+'"}' , headers=headers)
        print('Submitted email')
        self.shipping(c , lines)

    def shipping(self, c , lines):
        shippingpage = c.get('https://www.footpatrol.com/checkout/delivery/', headers=headers)
        soup = bs(shippingpage.text, 'html.parser')
        get_id = soup.find('input', {'name':'cartDeliveryMethodId'})
        tkn = get_id['value']
        data1 = ('{"deliveryMethodID":"'+tkn+'","deliveryLocation":"gb"}')
        delid = c.put('https://www.footpatrol.com/cart/' , data = data1 , headers=headers)
        print('Selected delivery method')
        self.shippinginfo(c , lines , tkn)

    def shippinginfo(self, c , lines , tkn):
        full_name = lines[0].strip('\n')
        fn,ln = full_name.split(" ", 1)
        number = lines[1].strip('\n')
        addy = lines[2].strip('\n')
        town = lines[9].strip('\n')
        pst = lines[10].strip('\n')
        data = ('{"useDeliveryAsBilling":true,"country":"United Kingdom|gb","locale":"","firstName":"'+fn+'","lastName":"'+ln+'","phone":"'+number+'","address1":"'+addy+'","address2":"","town":"'+town+'","county":"","postcode":"'+pst+'","addressPredict":"","setOnCart":"deliveryAddressID"}')
        ship = c.post('https://www.footpatrol.com/myaccount/addressbook/add/' , data = data , headers=headers)
        shipping = ship.text
        print('Submitted delivery details')
        self.id(c , tkn , shipping)

    def id(self, c , tkn, shipping):
        js1 = json.loads(shipping)
        addy1 = (js1['ID'])
        data2 = ('{"addressId":"'+addy1+'","methodId":"'+tkn+'","deliverySlot":{}}')
        conf = c.post('https://www.footpatrol.com/checkout/updateDeliveryAddressAndMethod/ajax/' , data = data2, headers=headers)
        self.addyID(c , addy1)



    def addyID(self , c , addy1):
        billing = c.get('https://www.footpatrol.com/checkout/billing/' , headers=headers)
        asd = c.post('https://www.footpatrol.com/checkout/updateBillingAddress/ajax/' , data = '{"editAddressID":"'+addy1+'"}', headers=headers)
        self.getayden(c)

    def getayden(self, c):
        print('Trying to go to ayden')
        asd1 = c.post('https://www.footpatrol.com/checkout/paymentV3/' , data = 'paySelect=card' , headers=headers)
        print(asd1.text)
        if 'adyen' in asd1.text:
            print('Found ayden checkout page')
            soup = bs(asd1.text, 'html.parser')
            get_id1 = soup.find('iframe', {'class':'paymentFrame'})
            tkn1 = str(get_id1['src'])
            newstr =  tkn1.replace('¤' , '&curren')
            self.ayden(c, newstr)
        if 'Cart with ID' in asd1.text:
            print('Cart unavailable - Going back to capctha')
            self.captcha(c)
        if 'there was no ID to use' in asd1.text:
            print('Cart unavailable - Going back to capctha')
            self.captcha(c)
        else:
            self.getayden(c)
        
    def ayden(self ,c , newstr):
        ayden = c.get(newstr , headers=headers)
        soup = bs(ayden.text, 'html.parser')
        sig = soup.find('input', {'name':'sig'})
        sig1 = sig['value']
        mr = soup.find('input', {'name':'merchantReference'})
        mr1 = mr['value']
        bc = soup.find('input', {'name':'brandCode'})
        bc1 = bc['value']
        pa = soup.find('input', {'name':'paymentAmount'})
        pa1 = pa['value']
        cc = soup.find('input', {'name':'currencyCode'})
        cc1 = cc['value']
        sbd = soup.find('input', {'name':'shipBeforeDate'})
        sbd1 = sbd['value']
        sc = soup.find('input', {'name':'skinCode'})
        sc1 = sc['value']
        ma = soup.find('input', {'name':'merchantAccount'})
        ma1 = ma['value']
        sl = soup.find('input', {'name':'shopperLocale'})
        sl1 = sl['value']
        stage = soup.find('input', {'name':'sessionId'})
        stage1 = stage['value']
        si = soup.find('input', {'name':'sessionId'})
        si1 = si['value']
        sv = soup.find('input', {'name':'sessionValidity'})
        sv1 = sv['value']
        se = soup.find('input', {'name':'shopperEmail'})
        se1 = se['value']
        sr = soup.find('input', {'name':'shopperReference'})
        sr1 = sr['value']
        rc = soup.find('input', {'name':'recurringContract'})
        rc1 = rc['value']
        ru = soup.find('input', {'name':'resURL'})
        ru1 = ru['value']
        am = soup.find('input', {'name':'allowedMethods'})
        am1 = am['value']
        bm = soup.find('input', {'name':'blockedMethods'})
        bm1 = bm['value']
        os = soup.find('input', {'name':'originalSession'})
        os1 = os['value']
        bast = soup.find('input', {'name':'billingAddress.street'})
        bast1 = bast['value']
        bahn = soup.find('input', {'name':'billingAddress.houseNumberOrName'})
        bahn1 = bahn['value']
        bacity = soup.find('input', {'name':'billingAddress.city'})
        bacity1 = bacity['value']
        bapc = soup.find('input', {'name':'billingAddress.postalCode'})
        bapc1 = bapc['value']
        basop = soup.find('input', {'name':'billingAddress.stateOrProvince'})
        basop1 = basop['value']
        bauk = soup.find('input', {'name':'billingAddress.country'})
        bauk1 = bauk['value']
        batt = soup.find('input', {'name':'billingAddressType'})
        batt1 = batt['value']
        bas = soup.find('input', {'name':'billingAddressSig'})
        bas1 = bas['value']
        dast = soup.find('input', {'name':'deliveryAddress.street'})
        dast1 = dast['value']
        dahn = soup.find('input', {'name':'deliveryAddress.houseNumberOrName'})
        dahn1 = dahn['value']
        dacity = soup.find('input', {'name':'deliveryAddress.city'})
        dacity1 = dacity['value']
        dapc = soup.find('input', {'name':'deliveryAddress.postalCode'})
        dapc1 = dapc['value']
        dasop = soup.find('input', {'name':'deliveryAddress.stateOrProvince'})
        dasop1 = dasop['value']
        daco = soup.find('input', {'name':'deliveryAddress.country'})
        daco1 = daco['value']
        daty = soup.find('input', {'name':'deliveryAddressType'})
        daty1 = daty['value']
        das = soup.find('input', {'name':'deliveryAddressSig'})
        das1 = das['value']
        sfn = soup.find('input', {'name':'shopper.firstName'})
        sfn1 = sfn['value']
        sln = soup.find('input', {'name':'shopper.lastName'})
        sln1 = sln['value']
        df = soup.find('input', {'name':'dfValue'})
        df1 = df['value']
        uf = soup.find('input', {'name':'usingFrame'})
        uf1 = uf['value']
        up = soup.find('input', {'name':'usingPopUp'})
        up1 = up['value']
        sbl = soup.find('input', {'name':'shopperBehaviorLog'})
        sbl1 = sbl['value']
        mit = soup.find('input', {'name':'merchantIntegration.type'})
        mit2 = mit['value']
        file = open('settings.txt' , 'r')
        lines = file.readlines()
        ccn = lines[4].strip('\n')
        ccname = lines[0].strip('\n')
        cem = lines[6].strip('\n')
        cey = lines[7].strip('\n')
        cvc = lines[5].strip('\n')
        aydendata = {
            'displayGroup': 'card',
            'card.cardNumber': ccn,
            'card.cardHolderName':ccname,
            'card.expiryMonth': cem,
            'card.expiryYear': cey,
            'card.cvcCode': cvc,
            'sig': sig1,
            'merchantReference': mr1,
            'brandCode': 'brandCodeUndef',
            'paymentAmount': pa1,
            'currencyCode': cc1,
            'shipBeforeDate': sbd1,
            'skinCode': sc1,
            'merchantAccount': 'JD_FootPatrol',
            'shopperLocale': 'gb',
            'stage': 'pay',
            'sessionId': si1,
            'sessionValidity': sv1,
            'shopperEmail': se1,
            'shopperReference': sr1,
            'recurringContract': '',
            'resURL': 'https://www.footpatrol.com/checkout/landing/',
            'allowedMethods':'card',
            'blockedMethods':bm1,
            'originalSession': os1,
            'billingAddress.street': bast1,
            'billingAddress.houseNumberOrName': bahn1,
            'billingAddress.city': bacity1,
            'billingAddress.postalCode': bapc1,
            'billingAddress.stateOrProvince': basop1,
            'billingAddress.country': 'GB',
            'billingAddressType': '2',
            'billingAddressSig': bas1,
            'deliveryAddress.street': dast1,
            'deliveryAddress.houseNumberOrName': dahn1,
            'deliveryAddress.city': dacity1,
            'deliveryAddress.postalCode': dapc1,
            'deliveryAddress.stateOrProvince': dasop1,
            'deliveryAddress.country': 'GB',
            'deliveryAddressType': '2',
            'deliveryAddressSig': das1,
            'shopper.firstName': sfn1,
            'shopper.lastName': sln1,
            'merchantIntegration.type': mit2,
            'referrerURL': 'https://www.footpatrol.com/checkout/billing/',
            'dfValue':'',
            'usingFrame': 'false',
            'usingPopUp': 'false',
            'shopperBehaviorLog': ''
            }
        ppp = input('Press enter to cop')
        payment = c.post('https://live.adyen.com/hpp/completeCard.shtml', data=aydendata , headers=headers)
        print(payment.url)
        if '3ds' in payment.text:
            print('Handling 3ds...')
            soup = bs(payment.text, 'html.parser')
            purl1 = soup.find('form', {'id':'pageform'})
            purl2 = purl1['action']
            pareq = soup.find('input', {'name':'PaReq'})
            pareq1 = pareq['value']
            MD = soup.find('input', {'name':'MD'})
            MD1 = MD['value']
            datafin1 = {
                'PaReq':pareq1,
                'TermUrl': 'https://live.adyen.com/hpp/complete3d.shtml',
                'MD':MD1,
                'shopperBehaviorLog':''
                }
            fin1 = c.post(purl2 , data = datafin1 , headers=headers)
            soup = bs(fin1.text, 'html.parser')
            pares = soup.find('input', {'name':'PaRes'})
            pares1 = pares['value']
            MD = soup.find('input', {'name':'MD'})
            MD1 = MD['value']
            datafinal = {
                'PaRes':pares1,
                'MD':MD1
                }
            payment = c.post('https://live.adyen.com/hpp/complete3d.shtml' , data=datafinal , headers=headers) 
        if 'REFUSED' in payment.url:
            print('Payment failed!')
        if 'queue' in payment.text:
            q = input('New cookie needed')
            c.cookies['akavpau_VP1'] = q
            c.get(payment.url , headers=headers)
            print('Check email')
        else:
            print('Check Email!')
            input()
        
        
        
        
        
        
        

    
        
        
            
    
    





for i in range(25):
    tasks = threading.Thread(target=task)
    tasks.start()
    
