import sqlite3, hashlib, os

# Open database
conn = sqlite3.connect('database.db')

#Populating user information
userdata = [(hashlib.md5('password'.encode()).hexdigest(), 'IHeartShopping123', 'e@e.com', 'Bob', 'Joe', 'Will', '123 Main St', 12345, 'Sunny', 'TX', 1234567890),
            (hashlib.md5('p@$$w0rd'.encode()).hexdigest(), 'DogzRKewl', 'user@user.com', 'Tom', 'Jones', 'Johnny', '100 1st St', 98765, 'Cloudy', 'WA', 1597534682),
            (hashlib.md5('catz'.encode()).hexdigest(), 'CatzRKewlR', 'catzz@user.com', 'Rev', 'Ike', 'Jordan', '40 Best St', 43975, 'Stormy', 'OR', 1973465215),
            (hashlib.md5('Aquasp'.encode()).hexdigest(), 'Aquasp', 'q@q.com', 'Eric', 'q', 'Mendez', '123 6th St.', 32904, 'Melbourne', 'FL', 2515469442),
            (hashlib.md5('123'.encode()).hexdigest(), 'TW123', 't@t.com', 'Tom', 'K', 'Williams', '125 6th St.',32907, 'Dallas', 'TX', 1234567891)]
conn.executemany('INSERT INTO users (password, username, email, firstName, middleName, lastName, address, zipcode, city, state, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',userdata)

#Populating user billing information
billingdata = [(1, 1234567890123456, 741, '2020-06-03', '2473 Waterview Lane', 'Roswell', 88201, 'NM'),
            (2, 4539440832303812, 963, '2019-06-04', '2828 Ashton Lane', 'Austin', 78701, 'TX'),
            (3, 5141078823820647, 429, '2021-06-05', '1431 Michigan Avenue', 'Pittsburgh', 15212, 'PA'),
            (4, 373613474700100, 734, '2018-09-26', '44 Shirley Ave.', 'West Chicago', 60185, 'IL'),
            (5, 4561238974561258, 569, '2022-09-16', '125 6th St','Dallas',32907, 'TX')
               ]
conn.executemany('INSERT INTO purchaseInfo (userId, creditCardNum, CCV, expDate, billAddr, billCity, billZip, billSt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',billingdata)

#Populating department information
depdata = [(10, 'Shoe', 'shoes/shoeDept.jpg'),
            (20, 'Jewelery', 'jewelery/jewelDept.jpg'),
            (30, 'Accessory', 'accessories/accessDept.jpg')]
conn.executemany('''INSERT INTO departments (depId, name, image) VALUES (?, ?, ?)''', depdata)

#Populating category information
catdata = [(11, 'Women', 10, 'shoes/womens/Womens.jpg'),
            (12, 'Men', 10, 'shoes/mens/Mens.jpg'),
            (13, 'Children', 10, 'shoes/childrens/Childrens.jpg'),
            (21, 'Necklace', 20, 'jewelery/necklaces/necklaces.jpg'),
            (22, 'Ring', 20, 'jewelery/rings/rings.jpg'),
            (23, 'Bracelet', 20, 'jewelery/bracelets/bracelets.jpg'),
            (31, 'Hat', 30, 'accessories/hats/hats.jpg'),
            (32, 'Sunglasses', 30, 'accessories/sunglasses/sunglasses.jpg'),
            (33, 'Purse', 30, 'accessories/purses/purses.jpg')]
conn.executemany('''INSERT INTO categories (categoryId, name, depId, image) VALUES (?, ?, ?, ?)''', catdata)

#Populating product information
proddata = [('Ugly Shoes', 10.99, 'Gucci', 'shoes/womens/uglyshoes.jpg', 20, 3, 11, 'Shiny, ugly shoes', True),
            ('90\'s Purse', 500.00, 'Designer', 'accessories/purses/uglypurse.jpg', 5, 5, 33, 'Very childish purse',False),
            ('Charm Bracelet', 100.50, 'Charming Charlies', 'jewelery/bracelets/charm_bracelet.jpg', 30, 5, 23, 'Very childish purse',False),
            ('Infinity Bracelet', 23.50, 'Claire\'s', 'jewelery/bracelets/infinity_bracelet.jpg', 10, 4, 23, 'This bracelet goes on forever',False),
            ('Rose Gold Bracelet', 3.50, 'Aggieland Outfitters', 'jewelery/bracelets/rose_gold_bracelet.jpg', 50, 5, 23, 'The rosiest of gold',True),
            ('Cheetah Pattern Raybans', 160.50, 'Raybans', 'accessories/sunglasses/rayban_sunglasses_pattern.jpg', 10, 5, 32, "Ain't no rays getting to your eyes",False),
            ('Solid Black Raybans', 60.50, 'Raybans', 'accessories/sunglasses/rayban_sunglasses.jpg', 70, 5, 32,'Classic Look',False),
            ('White Quay Sunglasses', 60.50, 'Quay', 'accessories/sunglasses/quay_sunglasses.jpg', 30, 2, 32, 'Statement Piece',True),
            ('Boots', 40.99, 'Hunter Boots Ltd', 'shoes/womens/boots.jpg', 10, 4, 11, 'Knee length boots', True),
            ('Flat Heel Shoes', 20.99, 'Silcon', 'shoes/womens/flat_heel.jpg', 16, 5, 11, 'Comfortable flat heeled open shoes', False),
            ('Flat Shoes', 12.99, 'SOREL', 'shoes/womens/flats.jpg', 12, 4, 11, 'Daily wear open shoes', True),
            ('Sneakers', 45.59, 'Nike', 'shoes/womens/nike.jpg', 21, 5, 11, 'Running Shoes', True),
            ('Party wear Heels', 34.99, 'Gucci', 'shoes/womens/party.jpg', 15, 4, 11, 'Stylish Party wear', True),
            ('Casual Shoes', 24.99, 'Addidas', 'shoes/mens/casual.jpg', 10, 5, 12, 'Casual wear shoes', True),
            ('Formal Shoes', 64.99, 'Jack Rogers', 'shoes/mens/formal_black.jpg', 10, 4, 12, 'Formal wear shoes', False),
            ('Sneakers', 24.99, 'Puma', 'shoes/mens/grey.jpg', 18, 4, 12, 'Running shoes', True),
            ('Sneakers', 44.99, 'New Balance', 'shoes/mens/new_bal.jpg', 14, 5, 12, 'Running shoes', True),
            ('Leather Shoes', 79.99, 'Lacoste', 'shoes/mens/leather.jpg', 18, 4, 12, 'Faux Leather shoes', False),
            ('Casual Navy Shoes', 25.99, 'Keds', 'shoes/mens/navy.jpg', 25, 5, 12, 'Casual navy blue shoes', True),
            ('Bow Shoe', 30.00, 'Acorn', 'shoes/childrens/blue_kid.jpg', 15, 5, 13, 'Cute shoes with bow', True),
            ('Boys Casual Wear', 30.00, 'FootMates', 'shoes/childrens/boys.jpg', 20, 4, 13, 'Casual wear for boys', True),
            ('LightUp Shoes', 35.00, 'Heelys', 'shoes/childrens/lightup.jpg', 23, 4, 13, 'LightUp Shoes for boys and girls', False),
            ('Open Toe Shoes', 20.00, 'Chole', 'shoes/childrens/pink_girl.jpg', 5, 4, 13, 'Pink open toe shoes for girls', True),
            ('Rainbow Slippers', 20.49, 'Converse', 'shoes/childrens/slippers.jpg', 15, 5, 13, 'Rainbow colored slippers', True),
            ('Sneaker', 30.00, 'Puma', 'shoes/childrens/sneaker.jpg', 10, 5, 13, 'Running shoes', True),
            ('Glittery Backpack', 100.00, 'ALDO', 'accessories/purses/backpack.jpg', 8, 4, 33, 'Cute Backpack',True),
            ('Mens Wallet', 70.69, 'Tommy Hilfiger', 'accessories/purses/brown.jpg', 3, 5, 33, 'Wallet',True),
            ('Handbag', 50.00, 'Fossil', 'accessories/purses/pink.jpg', 9, 4, 33, 'Pink Handbag',False),
            ('Sling Bag', 150.00, 'Roxy', 'accessories/purses/purple.jpg', 24, 5, 33, 'Purple Sling Bag',True),
            ('Minion Sling', 65.99, 'Tumi', 'accessories/purses/sling.jpg', 6, 4, 33, 'Cute Sling bag',False),
            ('Baseball Cap', 25.00, 'Designer', 'accessories/hats/baseball.jpg', 5, 5, 31, 'Stylish baseball cap',False),
            ('Ladies Cap', 30.00, 'Chole', 'accessories/hats/cap.jpg', 30, 4, 31, 'Black ladies cap',True),
            ('Winter Cap', 55.50, 'Eddie Baur', 'accessories/hats/eddie.jpg', 5, 5, 31, 'Winter shield',False),
            ('SilkFlower Hat', 50.00, 'Kipling', 'accessories/hats/silkflower.jpg', 5, 5, 31, 'Beautiful hat made of silk',True),
            ('Beaded Necklace', 60.50, 'Nina', 'jewelery/necklaces/beads.jpg', 5, 5, 21, 'White pearl necklace',False),
            ('Heart Necklace', 45.50, 'Kendra Scott', 'jewelery/necklaces/heart.jpg', 10, 4, 21, 'Silver heart pendant on long chain',False),
            ('Moon Pendant', 40.00, 'Miseno', 'jewelery/necklaces/moon.jpg', 15, 5, 21, 'Black metal Cresant pendant',True),
            ('Owl Pedant', 30.50, 'Eddie Baur', 'jewelery/necklaces/owl.jpg', 8, 4, 21, 'Stylish owl pendant',False),
            ('Butterfly Ring', 25.00, 'Kipling', 'jewelery/rings/butterfly.jpg', 5, 4, 22, 'Silver butterfly ring',True),
            ('Crown Ring', 150.00, 'Miseno', 'jewelery/rings/crown.jpg', 5, 5, 22, 'Rare white gold crown ring',True),
            ('Mother Ring', 75.00, 'Versace', 'jewelery/rings/mothers.jpg', 3, 5, 22, 'Wonderful gift for Mothers Day',True)]
conn.executemany('''INSERT INTO products (name, price, brand, image, stock, avgRating, categoryId, description, freeShip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', proddata)
cur = conn.cursor()
#Populating purchase history information
#Populating purchase history information
histdata = [(1, 1, 1, 10.99, '2018-07-16 10:05'),
                (2, 2, 5, 2500, '2021-01-27 12:55'),
                (2, 1, 2, 21.98, '2021-02-15 08:45'),
                (2, 11, 1, 12.99, '2018-02-17 03:05'),
                (1, 20, 1, 25.99, '2018-07-01 02:45'),
                (2, 4, 1, 23.50, '2018-04-10 08:45'),
                (2, 36, 2, 100.00, '2021-02-15 12:15'),
                (1, 41, 3, 75.00, '2021-02-15 4:30'),
                (1, 10, 1, 20.99, '2020-08-09 5:18'),
                (1, 23, 2, 70.00, '2019-12-20 4:30')]
conn.executemany('''INSERT INTO purchaseHistory (userId, productId, quantity, total, purDate) VALUES (?, ?, ?, ?, ?)''', histdata)



#Populating feedback information
feedbackdata = [(1, 1, 3, 'These were so painful, but man! They look fantastic!'),
                (2, 2, 5, 'This was the talk of the party!'),
                (2, 1, 3, 'Buy these shoes if you want a lot of pain'),
                (3, 1, 2, 'Nice!!'),
                (4, 2, 5, 'Wonderful'),
                (2, 3, 4, 'Beautiful!!'),
                (2, 4, 3, 'Love It'),
                (4, 5, 2, 'Not So Good'),
                (1, 6, 5, 'Perfect!!'),
                (2, 7, 4, 'Amazing'),
                (1, 8, 5, 'Nice'),
                (1, 9, 4, 'Love it'),
                (4, 10, 4, 'Too Good'),
                (3, 11, 1, 'Ok-Ok'),
                (1, 12, 2, 'Do Not Buy'),
                (1, 13, 3, 'Must Try'),
                (1, 14, 4, 'Amazing'),
                (1, 15, 4, 'Nice'),
                (2, 16, 4, 'Very Nice'),
                (2, 17, 3, 'Cute'),
                (2, 18, 3, 'Superb'),
                (2, 19, 4, 'Must Try'),
                (2, 20, 5, 'Amazing'),
                (3, 21, 4, 'Nice!!!!!'),
                (2, 22, 5, 'Wonderful!!'),
                (1, 23, 4, 'Fantastic.....'),
                (2, 24, 1, 'Very Bad'),
                (2, 25, 2, 'very expensive'),
                (2, 36, 5, 'Beautiful hat to wear for party.'),
                (1, 41, 4, 'Makes a wonderful gift. Gave it as a birthday gift to my daughter.'),
                (1, 23, 2, 'Bought 2 for my kids. The lights were dim and stopped working after 1 month.'),
                (1, 10, 4, 'Comfortable shoes. Stylish wear for spring time')
                ]
conn.executemany('''INSERT INTO feedback (userId, productId, rating, comment) VALUES (?, ?, ?, ?)''', feedbackdata)


conn.commit()
conn.close()