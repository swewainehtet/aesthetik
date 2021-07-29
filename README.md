# AESTHETIK
#### Video Demo: https://youtu.be/p7a6zLTzqRg
#### Description:
AESTHETIK is an online marketplace where users can enlist as either buyers or sellers.

## Buyer Features
- Buyers can view stores as they are being added
- Buyers can see if stores provide a discount for their items on the following store page
- Buyers can view the total cost after discounts (if any) and after taxes and fees
- When an item is being bought, an item's stock will drop by 1
- Any items with stock of 0 will be marked as sold out and will be prevented to being purchased
- Buyers can browse stores by category

## Seller Features
_In addition to buyer features sellers receive the following features_
- Sellers will be redirected to a first time store setup page if store hasn't been set up
- Sellers will get a unique page on the app called store portal (accessible to sellers only)
- Sellers can choose to reset their store information
- Sellers can add new listings
- Sellers can view their current listings from their portals
- Sellers can remove listings
- Stores can be accessed via a unique url `/store/url`

## Other Features
- Stores and products images are dynamically auto-generated
- Store page primary color will match the generated icon's
- Items can be only purchased via login (uers will be prompted to log in after clicking buy on a product)
- Home page can feature ads

## Technical Details
- This project is built using Flask, SQLite3, and Bootstrap
- Other services include: Gravatar, Python Image Library


## Tutorials

### Registering
- To register for an account click on "Register" on the menu or go to `/register`
- Enter user info when prompted
- If successful you will be redirected to the home page
- Otherwise, an apology message will be displayed indicating an error

### Logging in
- To log in you must first have an account via registering
- To log in click on "Log In" on the menu or go to `/login`
- If successful you will be redirected to the home page
- Otherwise, an apology message will be displayed indicating an error

### Store First time setup
- To setup a store you must first have an account via registering and must have a seller account
- To setup a store for the first time visit "Seller Portal" on the menu or go to `/portal`
- Enter information when prompted
- Once setup, the store can be viewd via `/store/<your store URL>`
- Store Icon will be uniquely auto-generated for you

### Store Management / Portal System
- To add items go to add items form and enter information when prompted
- Once items are added you can manage your inventory buy going to store inventory in the portal
- You can delete your listings by clicking on the "X" button on the right of the table in inventory
- Store information can be reset using the "[Reset Store Info]" button
- Your unqiue product ID and the icon will be uniquely auto-generated
- You can access your product via `/product/<your product ID>``

### Contact Us
- Clicking on the "Contact Us" button will lead to an email to service to our customer service team

##### By Swe Waine Htet for CS50x