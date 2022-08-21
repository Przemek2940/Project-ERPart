import psycopg2
from flask import Flask, render_template, request, redirect, url_for

conn = psycopg2.connect(
    database="Sprzedaz_magazynowa", user='postgres', password='postgres',
    host='projectsql.c4lilzenuyna.eu-central-1.rds.amazonaws.com', port='5432')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view_availability')
def view_availability():
    query = """select g.id_group, g.name_group, i.id_item, i.name_item, 
                sum((case when a.item_quant is null then 0 else a.item_quant end)) 
                from availability a
                    right join items i on a.id_item =  i.id_item
                    left join item_groups g on i.id_group = g.id_group
                group by i.id_item, g.id_group
                order by g.id_group, i.id_item"""
    cur = conn.cursor()
    cur.execute(query)
    ava = cur.fetchall()

    return render_template('availability_list.html', ava=ava)


@app.route('/availability_add', methods=['GET', 'POST'])
def availability_add():
    if request.method == 'POST':
        id_item = request.form.get("id_item")
        quant = request.form.get("quant")

        cur = conn.cursor()
        cur.execute('INSERT INTO availability(id_item, item_quant) VALUES (%s,%s)', (id_item, quant))
        conn.commit()
        cur.close()
        conn.close()
        print("Dodano")
        return redirect(url_for('index'))

   # return render_template('availability_list.html')


if __name__ == '__main__':
    app.run(debug=True)


