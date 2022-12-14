import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for

conn = psycopg2.connect(
    database="loc_project", user='postgres', password='admin',
    host='localhost', port='5432')


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rebuilding')
def rebuilding():
    return render_template('rebuilding.html')


@app.route('/view_availability')
def view_availability():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """select g.id_group, g.name_group, i.id_item, i.name_item, 
                sum((case when w.item_quant is null then 0 else w.item_quant end)) 
                from warehouse w
                    right join items i on w.id_item =  i.id_item
                    left join item_groups g on i.id_group = g.id_group
                group by i.id_item, g.id_group
                order by g.id_group, i.id_item"""
    cur.execute(query)
    ava = cur.fetchall()

    return render_template('availability_list.html', ava=ava)


@app.route('/availability_add', methods=['GET', 'POST'])
def availability_add():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        table_item = """select id_item from items"""
        cur.execute(table_item)
        table_it = cur.fetchall()
        id_item = int(request.form.get("id_item"))
        quant = int(request.form.get("quant"))

        if [id_item] not in table_it:
            error = "Nieprawidłowe ID. Spróbować ponownie?"
            return render_template('error.html', error=error)
        elif quant > 10000:
            error = "Zbyt duża ilość - maksymalny załadunek to 10tys. Spróbować ponownie?"
            return render_template('error.html', error=error)
        else:
            cur.execute('INSERT INTO availability(id_item, item_quant) VALUES (%s,%s)', (id_item, quant))
            conn.commit()
            return redirect(url_for('view_availability'))
    else:
        error = "Błąd przesyłu danych [54]."
        return render_template('error.html', error=error)


@app.route('/view_customers')
def view_customers():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """select id_customer, name_customer
                from customers
                order by id_customer"""
    cur.execute(query)
    cust = cur.fetchall()

    return render_template('customers.html', cust=cust)


@app.route('/customers_add', methods=['GET', 'POST'])
def customers_add():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        name_customer = request.form.get("name_customer")

        cur.execute('INSERT INTO customers(name_customer) VALUES (%s)', (name_customer,))
        conn.commit()
        return redirect(url_for('view_customers'))
    else:
        error = "Błąd przesyłu danych [54]."
        return render_template('error.html', error=error)


@app.route('/order_completing')
def order_completing():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query1 = """select g.id_group, g.name_group, i.id_item, i.name_item,
                sum((case when w.item_quant is null then 0 else w.item_quant end)), i.price_item||'zł' 
                from warehouse w
                    right join items i on w.id_item =  i.id_item
                    left join item_groups g on i.id_group = g.id_group
                group by i.id_item, g.id_group
                order by g.id_group, i.id_item"""
    cur.execute(query1)
    oc = cur.fetchall()

    query2 = """select id_customer, name_customer
                from customers
                order by id_customer"""
    cur.execute(query2)
    cop = cur.fetchall()
    return render_template('order.html', oc=oc, cop=cop)


@app.route('/order_saving')
def order_saving():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        return 0


if __name__ == '__main__':
    app.run(debug=True)
