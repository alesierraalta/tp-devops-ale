from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

notas = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nota = request.form['nota']
        notas.append(nota)
    return render_template('index.html', notas=notas)

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if 0 <= index < len(notas):
        if request.method == 'POST':
            notas[index] = request.form['nota']
            return redirect(url_for('index'))
        return render_template('edit.html', index=index, nota=notas[index])
    return redirect(url_for('index'))

@app.route('/delete/<int:index>', methods=['GET'])
def delete(index):
    if 0 <= index < len(notas):
        del notas[index]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
