from flask import Flask, render_template, request
application = Flask(__name__)


@application.route('/')
@application.route('/index')
def index():
    saved_folder = 'saved_data'
    date_string = '2011-02-14'  # default
    if request.args.get('date'):
        date_string = str(request.args.get('date'))
    return render_template('index.html', folder_name=saved_folder + '/' + date_string, default_date=date_string)

if __name__ == '__main__':
    application.run(debug=True)
