from flask import render_template, flash, redirect, url_for, session, g
from flask.views import MethodView

class DashboardAPI(MethodView):
    
    def get(self):
        if g.user:
            return render_template('dashboard.html')
        return redirect(url_for('login_api'))
