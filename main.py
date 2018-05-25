from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            isGuest = True
            email = "guest@guest.com"
            userId = -1
            userName = "guest"
            firstName = "Guest"
            middleName = ""
            lastName = "Guest"
            city = ""
            state = ""
            address = ""
            zipcode = ""
            phone = ""
        else:
            loggedIn = True
            isGuest = False
            cur.execute("SELECT userId, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone FROM users WHERE email = '" + session['email'] + "'")
            userInfo = cur.fetchone()
            userId, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone= userInfo
        cur.execute("SELECT count(distinct quantity) FROM kart WHERE userId = " + str(userId))
        noOfItems = cur.fetchone()[0]
        if noOfItems is None:
            noOfItems = 0
    conn.close()
    return (loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest)


@app.route("/")
def root():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT products.productId, products.name, products.price, products.brand, products.image, products.avgRating, products.stock, products.description, products.freeShip FROM products GROUP BY products.productId')
        itemData = cur.fetchall()
        comItemData = []
        for item in itemData:
            data = []
            for col in item:
                data.append(col)
            cur.execute('SELECT round(avg(feedback.rating),1) FROM products, feedback WHERE products.productId = feedback.productId AND products.productId = '+str(item[0])+' GROUP BY products.productId')
            feedData = cur.fetchone()
            if feedData == None:
                data.append(0)
            else:
                data.append(feedData[0])
            comItemData.append(data)
        cur.execute('SELECT categoryId, name, image FROM categories')
        categoryData = cur.fetchall()
        cur.execute('SELECT depId, name, image FROM departments')
        departmentData = cur.fetchall()
        itemData = comItemData
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, userName=userName, firstName=firstName, noOfItems=noOfItems, departmentData=departmentData, categoryData=categoryData)

@app.route("/displayDepartment")
def displayDepartment():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    departmentId = request.args.get("depId")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categories.name,departments.name, categories.categoryId, categories.image  FROM categories, departments WHERE departments.depId = categories.depId AND departments.depId = " + departmentId + " GROUP BY categories.categoryId")
        data = cur.fetchall()
    conn.close()
    departmentName = data[0][1]
    data = parse(data)
    return render_template('displayDepartment.html', data=data, loggedIn=loggedIn, userName=userName, firstName=firstName, noOfItems=noOfItems, departmentName=departmentName)

@app.route("/displayCategory")
def displayCategory():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    categoryId = request.args.get("categoryId")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name, departments.name FROM products, categories, departments WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + categoryId + " GROUP BY products.productId")
        data = cur.fetchall()
        cur.execute("SELECT categories.name FROM products, categories, departments WHERE categories.categoryId = " + categoryId)
        cat_name = cur.fetchall()
        categoryName = cat_name[0][0]
    conn.close()
    data = parse(data)
    return render_template('displayCategory.html', data=data, loggedIn=loggedIn, userName=userName, firstName=firstName, categoryName = categoryName, noOfItems=noOfItems)

@app.route("/account/profile")
def profileHome():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    if 'email' not in session:
        return redirect(url_for('root'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT products.name, purchaseHistory.quantity, purchaseHistory.total, purchaseHistory.purDate  FROM purchaseHistory, products WHERE purchaseHistory.productId = products.productId AND purchaseHistory.userId = " + str(userId) + " ORDER BY purchaseHistory.purDate DESC")
        data = cur.fetchall()
    conn.close()
    return render_template("profileHome.html", loggedIn=loggedIn, userName=userName, firstName=firstName, lastName=lastName, email=email, city=city, state=state, noOfItems=noOfItems, data=data)

@app.route("/receipt")
def receipt():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            isGuest = True
            userId = -1
            cur.execute("SELECT * FROM users WHERE userId = -1")
            userInfo = cur.fetchone()
            userId, password, userName, email, firstName, middleName, lastName, address, zipcode, city, state, phone = userInfo
        else:
            # return redirect(url_for('loginForm'))
            loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
            cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
            userId = cur.fetchone()[0]
            if noOfItems is None:
                noOfItems = 0
        cur.execute("SELECT products.productId, products.name, products.price, products.image, kart.quantity, (kart.quantity*products.price), products.freeShip FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        totalPrice = 0
        noOfItems = 0
        for product in products:
            cur.execute("INSERT INTO purchaseHistory (userId, productId, quantity, total, purDate) VALUES (?, ?, ?, ?, ?)", (userId, product[0], product[4], product[5], today))
            cur.execute("UPDATE products SET stock = (stock - ?) WHERE productId = ?", (product[4], product[0]))
            cur.execute("DELETE FROM kart WHERE userId = " + str(userId))
            totalPrice += (product[2] * product[4])
            noOfItems += 1
        subTotal = 0
        shipping = 0
        delivery = False
        has_items = len(products) != 0
        if noOfItems is None:
            noOfItems = 0
        for row in products:
            subTotal += (row[2] * row[4])
            if not bool(row[6]):
                delivery = bool(row[6])
                shipping += (row[2] * row[4]) * 0.1
        totalPrice = subTotal + shipping
        noOfItems = 0
        subTotal = round(subTotal, 2)
        #print subTotal, shipping, totalPrice

    return render_template("receipt.html", totalPrice=totalPrice, shipping=shipping, subTotal=subTotal, loggedIn=loggedIn,
                           userName=userName, firstName=firstName, lastName=lastName, email=email,
                           address=address, zipcode=zipcode, city=city, state=state,
                           noOfItems=noOfItems, products=products, delivery=delivery,phone=phone,
                           orderDate=today)

@app.route("/billing", methods=["GET", "POST"])
def billing():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    if 'email' not in session:
        email = 'guest@guest.com'
        userId = -1
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT users.userId, email, username, firstName, middleName, lastName, address, zipcode, city, state, phone FROM purchaseInfo, users WHERE purchaseInfo.userId = users.userId AND email = '" + email + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("billing.html", profileData=profileData, loggedIn=loggedIn, userName=userName, firstName=firstName, lastName=lastName, email=email, city=city, state=state, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, username, firstName, middleName, lastName, address, zipcode, city, state, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
        cur.execute("SELECT creditCardNum, CCV, expDate, billAddr, billCity, billZip , billSt FROM purchaseInfo WHERE userId = '" + str(userId) + "'")
        billingData = cur.fetchone()
        #print billingData
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, userName=userName, firstName=firstName, lastName=lastName, email=email, city=city, state=state, noOfItems=noOfItems, billingData=billingData)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = '" + session['email'] + "'")
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Password Changed successfully!!!"
                except:
                    conn.rollback()
                    msg = "Failed to Change the Password!!!"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Failed to Change the Password!!!"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")


@app.route("/updateGuestBilling", methods=["GET", "POST"])
def updateGuestBilling():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        ccn = request.form['ccn']
        ccv = request.form['ccv']
        expDate = request.form['expDate']
        billingAddress = request.form['billingAddress']
        billingCity = request.form['billingCity']
        billingState = request.form['billingState']
        billingZip = request.form['billingZip']
        loggedIn = False
        userId = -1
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('INSERT OR REPLACE INTO purchaseInfo(userId, creditCardNum, CCV, expDate, billAddr, billCity, billZip, billSt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (userId, ccn, ccv, expDate, billingAddress, billingCity, billingState, billingZip))
                    con.commit()
                    cur = con.cursor()
                    cur.execute(
                        "SELECT creditCardNum, CCV, expDate, billAddr, billCity, billSt, billZip FROM purchaseInfo WHERE userId = '" + str(
                            userId) + "'")
                    billingData = cur.fetchone()
                    cur = con.cursor()
                    cur.execute('INSERT OR REPLACE INTO users (userId, password, userName, email, firstName, middleName, lastName, address, zipcode, city, state, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                (userId, '', 'Guest', email, firstName, '', lastName, billingAddress, billingZip, billingCity, billingState, 0))
                    con.commit()
                    msg = "Billing Info Saved Successfully"
                except Exception as e:
                    #print "ERROR", e
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('checkout'))

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    if request.method == 'POST':
        firstName = request.form['firstName']
        middleName = request.form['middleName']
        lastName = request.form['lastName']
        address = request.form['address']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']

        ccn = request.form['ccn']
        ccv = request.form['ccv']
        expDate = request.form['expDate']
        billingAddress = request.form['billingAddress']
        billingCity = request.form['billingCity']
        billingState = request.form['billingState']
        billingZip = request.form['billingZip']
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET email = ?, userName = ?, firstName = ?, middleName = ?, lastName = ?, address = ?, zipcode = ?, city = ?, state = ?, phone = ? WHERE email = ?',(email, userName, firstName, middleName, lastName, address, zipcode, city, state, phone, email))
                    con.commit()
                    msg = "Profile Info Saved Successfully!!"
                    cur = con.cursor()
                    cur.execute('UPDATE purchaseInfo SET creditCardNum = ?, CCV = ?, expDate = ?, billAddr = ?, billCity = ?, billZip = ?, billSt = ?',
                                (ccn, ccv, expDate, billingAddress, billingCity, billingState, billingZip))

                    con.commit()
                    msg = "Information Saved Successfully!!"
                except:
                    con.rollback()
                    msg = "Error occured!!"
                cur = con.cursor()
                cur.execute("SELECT userId, email, username, firstName, middleName, lastName, address, zipcode, city, state, phone FROM users WHERE email = '" + session['email'] + "'")
                profileData = cur.fetchone()
                cur.execute("SELECT creditCardNum, CCV, expDate, billAddr, billCity, billSt, billZip FROM purchaseInfo WHERE userId = '" + str(userId) + "'")
                billingData = cur.fetchone()
                #print billingData
                ##print profileData
        con.close()
        return render_template("editProfile.html", msg = msg, profileData=profileData, loggedIn=loggedIn, userName=userName, firstName=firstName, lastName=lastName, email=email, city=city, state=state,noOfItems=noOfItems,billingData=billingData)
        #return redirect(url_for('editProfile'))

@app.route("/checkout")
def checkout():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    delivery = request.args.get("deliveryMethod")
    delivery = (delivery == "home")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' in session:
            cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
            userId = cur.fetchone()[0]
            isGuest = False
        else:
            userId = -1
            isGuest = True
        cur.execute("SELECT products.productId, products.name, products.price, products.image, kart.quantity, (kart.quantity*products.price), products.freeShip FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
        cur.execute("SELECT creditCardNum, CCV, expDate, billAddr, billCity, billSt, billZip FROM purchaseInfo WHERE userId = '" + str(userId) + "'")
        billingData = list(cur.fetchone())
        #for i in range(3, len(billingData)):
        #    billingData[i] = billingData[i].upper()
    subTotal = 0
    shipping = 0
    has_items = len(products) != 0
    if noOfItems is None:
        noOfItems = 0
    for row in products:
        subTotal += (row[2] * row[4])
        if not bool(row[6]):
            shipping += (row[2] * row[4]) * 0.10
    subTotal = round(subTotal,2)
    totalPrice = subTotal + shipping
    return render_template("checkout.html", products = products, totalPrice=totalPrice, subTotal=subTotal, shipping=shipping, loggedIn=loggedIn, userName=userName, firstName=firstName, lastName=lastName, email=email, city=city, state=state, noOfItems=noOfItems, has_items = has_items, billingData=billingData, isGuest=isGuest, isHomeDeliver=delivery)

@app.route("/advSearch", methods = ['POST', 'GET'])
def advSearch():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' in session:
            cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
            userId = cur.fetchone()[0]
            isGuest = False
        else:
            userId = -1
            isGuest = True
            firstName = "Guest"
    return render_template('advSearch.html', loggedIn=loggedIn, userName=userName,firstName=firstName, noOfItems=noOfItems)

@app.route("/searchResults", methods = ['POST', 'GET'])
def searchResults():
    searchBy = request.args.get("searchBy")

    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        if searchBy == "rate":
            rating = request.args.get("rating")
            cur.execute(
               'SELECT products.productId, products.name, products.price, products.brand, products.image, products.avgRating, products.stock, products.description, products.freeShip '
               'FROM products WHERE products.avgRating >= '+str(rating)+' GROUP BY products.productId')
            #cur.execute('SELECT products.productId, products.name, products.price, products.brand, products.image, round(avg(feedback.rating),1), products.stock, products.description, products.freeShip'
            #            ' FROM products, feedback'
            #            ' WHERE products.productId = feedback.productId GROUP BY products.productId')
            itemData = cur.fetchall()
        if searchBy == "price":
            minPrice = request.args.get("minPrice")
            maxPrice = request.args.get("maxPrice")
            cur.execute(
                'SELECT products.productId, products.name, products.price, products.brand, products.image, products.avgRating, products.stock, products.description, products.freeShip '
                'FROM products WHERE products.price >= '+str(minPrice) +' AND products.price <= '+str(maxPrice)+' GROUP BY products.productId')
            itemData = cur.fetchall()
        if searchBy == 'brand':
            brandName = request.args.get("brandName")
            cur.execute(
            'SELECT products.productId, products.name, products.price, products.brand, products.image, products.avgRating, products.stock, products.description, products.freeShip '
            'FROM products WHERE upper(products.brand) LIKE "%' + str(
                brandName) + '%" GROUP BY products.productId')
            itemData = cur.fetchall()

        comItemData = []
        for item in itemData:
            data = []
            for col in item:
                data.append(col)
            cur.execute(
                'SELECT round(avg(feedback.rating),1) FROM products, feedback WHERE products.productId = feedback.productId AND products.productId = ' + str(
                item[0]) + ' GROUP BY products.productId')
            feedData = cur.fetchone()
            if feedData == None:
                data.append(0)
            else:
                data.append(feedData[0])
            comItemData.append(data)
        itemData = comItemData

    itemData = parse(itemData)
    return render_template('searchResults.html', itemData=itemData, loggedIn=loggedIn, userName=userName, firstName=firstName, noOfItems=noOfItems)

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/addComment", methods = ['GET', 'POST'])
def addComment():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]
            cur.execute("SELECT name FROM products WHERE productId = '" + str(productId) + "'")
            productName = cur.fetchone()[0]
        conn.close()
        return render_template('addComment.html', productId=productId, productName=productName, userId=userId)


@app.route("/updateComment", methods=["GET", "POST"])
def updateComment():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']
        productId = int(request.args.get('productId'))
        ###print 'PRODUCT ID', productId
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute( 'INSERT INTO feedback (userId, productId, rating, comment) VALUES (?, ?, ?, ?)',(userId, productId, rating, comment))
                    con.commit()
                    msg = "Saved Successfully!!"
                except Exception as e:
                    con.rollback()
                    msg = "Error Occurred!!", e
                cur = con.cursor()
                cur.execute("SELECT userId, email, username, firstName, middleName, lastName, address, zipcode, city, state, phone FROM users WHERE email = '" + session['email'] + "'")
        con.close()
        return redirect(url_for('root'))

@app.route("/productDescription")
def productDescription():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()

    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT products.productId, products.name, products.price, products.brand, products.image, products.stock, products.avgRating, products.description, products.freeShip FROM products WHERE products.productId = ' + productId + ' GROUP BY products.productId')
        productData = cur.fetchone()
        #print productData
        comItemData = []
        for item in productData:
            comItemData.append(item)
        cur.execute(
            'SELECT round(avg(feedback.rating),1) FROM products, feedback WHERE products.productId = feedback.productId AND products.productId = ' + str(
                productData[0]) + ' GROUP BY products.productId')
        feedData = cur.fetchone()
        if feedData == None:
            comItemData.append(0)
        else:
            comItemData.append(feedData[0])
        comItemData.append(comItemData)
        productData = comItemData
        freeShip = bool(productData[8])
        rating = int(productData[9])
        isAvail = (productData[5])
        #print productData, freeShip, rating, isAvail
        cur.execute('SELECT users.userName, feedback.rating, feedback.comment FROM products, users, feedback WHERE users.userId = feedback.userId AND feedback.productId = products.productId AND products.productId = ' + productId)
        commentData = cur.fetchall()
        isGuest = (userId == -1)
        #print isGuest
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn=loggedIn, commentData=commentData, isGuest=isGuest, freeShip = freeShip, rating=rating, isAvail=isAvail, userName=userName, firstName=firstName, lastName=lastName, email=email, city=city, state=state, noOfItems=noOfItems)


@app.route("/addToCart")
def addToCart():
    productId = int(request.args.get('productId'))

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            userId = -1
        else:
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]

        try:
            #cur = conn.cursor()
            cur.execute("SELECT quantity FROM kart WHERE productId = ? AND userId = ?", (productId, userId))
            count = cur.fetchone()
            print (productId, userId, count)

            if(count is None):
                count = 1
            else:
                count += 1
            cur.execute("INSERT INTO kart (userId, productId, quantity) VALUES (?, ?, ?)",
                            (userId, productId, count))
            conn.commit()
            cur = conn.cursor()
            cur.execute("SELECT quantity FROM kart WHERE productId = ? AND userId = ?", (productId, userId))
            count = cur.fetchone()
            print ("AFTER", count)
            msg = "Added successfully"
        except Exception as e:
            conn.rollback()
            msg = "Error occured"
            print ("ERROR", e)
    conn.close()
    #return render_template("home.html",noOfItems=noOfItems)
    return redirect(url_for('root'))

@app.route("/updateQuantity", methods=["GET", "POST"])
def updateQuantity():
    productId = int(request.args.get('productId'))
    operation = request.args.get('operation')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            userId = -1
        else:
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]
        try:
            cur.execute(
                "SELECT quantity FROM kart WHERE kart.userId = " + str(
                    userId) + " AND productId = " + str(productId))
            quantity = cur.fetchone()[0]
            if operation == 'add':
                quantity += 1
            else:
                quantity -= 1
            cur.execute("UPDATE kart SET quantity = " + str(quantity) + " WHERE userId = " + str(userId) + " AND productId = " + str(productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occurred"
    conn.close()
    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    loggedIn, userName, firstName, middleName, lastName, email, address, zipcode, city, state, phone, noOfItems, userId, isGuest = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        reachedMax = False
        if 'email' not in session:
            userId = -1
			#reachedMax = 1 == 1
		
        else:
            cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
            userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image, kart.quantity, (kart.quantity*products.price), products.stock FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    has_items = len(products) != 0
    if noOfItems is None:
        noOfItems = 0
    '''output = []
    
    for p in products[0]:
        output.append(p)
    products = output'''
    for row in products:
        totalPrice += (row[2] * row[4])
        reachedMax = row[4] == row[6]
        #x = round(int(row[5]),2)
        #row[5] = x
    totalPrice = round(totalPrice, 2)
   # noOfItems = noOfItems+1
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, userName=userName, firstName=firstName, lastName=lastName, email=email, city=city, state=state, noOfItems=noOfItems, has_items = has_items, isGuest=isGuest, reachedMax=reachedMax)

@app.route("/removeFromCart")
def removeFromCart():
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            userId = -1
        else:
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart WHERE userId = " + str(userId) + " AND productId = " + str(productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        userName = request.form['userName']
        firstName = request.form['firstName']
        middleName = request.form['middleName']
        lastName = request.form['lastName']
        address = request.form['address']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        billSave = request.form['save']
        ##print password, email, userName, firstName, middleName, lastName, address, zipcode, city, state, phone
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, userName, email, firstName, middleName, lastName, address, zipcode, city, state, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (hashlib.md5(password.encode()).hexdigest(), userName, email, firstName, middleName, lastName, address, zipcode, city, state, phone))
                con.commit()
                cur.execute("SELECT userId FROM users WHERE email = '" + email + "' AND userName = '" + userName +"'")
                userId = cur.fetchone()[0]
                if billSave == 'Yes':
                    print ("In if")
                    ccn = request.form['ccn']
                    ccv = request.form['ccv']
                    exDate = request.form['exDate']
                    bAddress = request.form['bAddress']
                    bCity = request.form['bCity']
                    bState = request.form['bState']
                    bZip = request.form['bZip']

                    cur.execute('INSERT INTO purchaseInfo (userId, creditCardNum, CCV, expDate, billAddr, billCity, billZip, billSt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                (userId, ccn, ccv, exDate, bAddress, bCity, bState, bZip))
                    print (userName, ccn, ccv, exDate, bAddress, bCity, bState, bZip)
                    con.commit()

                msg = "Registered Successfully"
            except sqlite3.Error as e:
                con.rollback()
                msg = e
        con.close()
        return render_template("login.html", error=msg)

@app.route("/addCommentForm")
def addCommentForm():
    return render_template("addComment.html")

@app.route("/registrationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == '__main__':
    app.run(debug=True)
