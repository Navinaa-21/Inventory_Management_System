# app.py
from flask import Flask, render_template, redirect, url_for, request
from models import db, Product, Location, ProductMovement
from forms import ProductForm, LocationForm, ProductMovementForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/inventory_db'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

# Product CRUD
@app.route('/products', methods=['GET', 'POST'])
def products():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(product_id=form.product_id.data, name=form.name.data)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    all_products = Product.query.all()
    return render_template('product.html', form=form, products=all_products)

# Location CRUD
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    form = LocationForm()
    if form.validate_on_submit():
        location = Location(location_id=form.location_id.data, name=form.name.data)
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('locations'))
    all_locations = Location.query.all()
    return render_template('location.html', form=form, locations=all_locations)

# Product Movement CRUD
@app.route('/movements', methods=['GET', 'POST'])
def movements():
    form = ProductMovementForm()
    if form.validate_on_submit():
        movement = ProductMovement(
            movement_id=form.movement_id.data,
            product_id=form.product_id.data,
            from_location=form.from_location.data or None,
            to_location=form.to_location.data or None,
            qty=form.qty.data
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for('movements'))
    all_movements = ProductMovement.query.all()
    return render_template('movement.html', form=form, movements=all_movements)

# Report
@app.route('/report')
def report():
    # Calculate balance per location
    products = Product.query.all()
    locations = Location.query.all()
    report_data = []

    for loc in locations:
        for prod in products:
            in_qty = db.session.query(db.func.sum(ProductMovement.qty)).filter_by(to_location=loc.location_id, product_id=prod.product_id).scalar() or 0
            out_qty = db.session.query(db.func.sum(ProductMovement.qty)).filter_by(from_location=loc.location_id, product_id=prod.product_id).scalar() or 0
            balance = in_qty - out_qty
            if balance > 0:
                report_data.append({'product': prod.name, 'location': loc.name, 'qty': balance})
    
    return render_template('report.html', report=report_data)

if __name__ == '__main__':
    app.run(debug=True)
