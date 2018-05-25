import sqlite3

# Open database
conn = sqlite3.connect('database.db')


# Create table
conn.execute('''DROP TABLE IF EXISTS kart''')
conn.execute('''DROP TABLE IF EXISTS purchaseHistory''')
conn.execute('''DROP TABLE IF EXISTS purchaseInfo''')
conn.execute('''DROP TABLE IF EXISTS feedback''')
conn.execute('''DROP TABLE IF EXISTS users''')
conn.execute('''DROP TABLE IF EXISTS products''')
conn.execute('''DROP TABLE IF EXISTS categories''')
conn.execute('''DROP TABLE IF EXISTS departments''')

conn.execute('''CREATE TABLE departments
        (depId INTEGER PRIMARY KEY,
        name TEXT,
        image TEXT
        )''')

conn.execute('''CREATE TABLE categories
        (categoryId INTEGER PRIMARY KEY,
        name TEXT,
        depId INTEGER,
        image TEXT,
        FOREIGN KEY(depId) REFERENCES departments
        )''')

conn.execute('''CREATE TABLE products
        (productId INTEGER PRIMARY KEY,
        name TEXT COLLATE NOCASE,
        price REAL,
        brand TEXT COLLATE NOCASE,
        image TEXT,
        stock INTEGER,
        avgRating REAL,
        categoryId INTEGER,
        description TEXT COLLATE NOCASE,
        freeShip BOOLEAN,
        FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
        )''')

conn.execute('''CREATE TABLE users 
        (userId INTEGER PRIMARY KEY, 
        password TEXT,
        userName TEXT,
        email TEXT,
        firstName TEXT,
        middleName TEXT,
        lastName TEXT,
        address TEXT,
        zipcode INTEGER,
        city TEXT,
        state TEXT,
        phone INTEGER
        )''')

conn.execute('''CREATE TABLE feedback
                (userId INTEGER,
                productId INTEGER,
                rating INTEGER,
                comment TEXT,
                FOREIGN KEY(userId) REFERENCES users(userId),
                FOREIGN KEY(productId) REFERENCES products(productId))''')

conn.execute('''CREATE TABLE purchaseInfo
        (userId INTEGER PRIMARY KEY, 
        creditCardNum INTEGER,
        CCV INTEGER,
        expDate TEXT,
        billAddr TEXT,
        billCity TEXT,
        billZip INTEGER,
        billSt TEXT,
        FOREIGN KEY(userId) REFERENCES users(userId)
        )''')

conn.execute('''CREATE TABLE purchaseHistory
                (userId INTEGER,
                productId INTEGER,
                quantity INTEGER,
                total REAL,
                purDate DATE,
                PRIMARY KEY(userId, productId, quantity, total, purDate),
                FOREIGN KEY(userId) REFERENCES users(userId),
                FOREIGN KEY(productId) REFERENCES products(productId))''')

conn.execute('''CREATE TABLE kart
        (userId INTEGER,
        productId INTEGER,
        quantity INTEGER,
        FOREIGN KEY(userId) REFERENCES users(userId),
        FOREIGN KEY(productId) REFERENCES products(productId)
        )''')

conn.close()