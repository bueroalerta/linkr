from flask import redirect
from flask import render_template
from flask import request

import database.link
from linkr import app
from uri.link import *
from uri.main import *
from util.decorators import require_form_args


@app.route(LinkAliasRedirectURI.path, methods=LinkAliasRedirectURI.methods)
@require_form_args([])
def alias_route(data, alias):
    # Attempt to fetch the link mapping from the database
    link = database.link.get_link_by_alias(alias)

    if not link:
        if request.method == 'GET':
            # For GET requests (likely from a browser), direct to the frontend interface
            return render_template('index.html')
        elif request.method == 'POST':
            # For POST requests (likely programmatic), send a plain-text response with an
            # appropriate status code
            return 'Link alias not found', 404

    # Redirect to the frontend interface to handle authentication for password-protected links
    if link.password_hash and not link.validate_password(data.get('password', '')):
        return render_template('index.html')

    database.link.add_link_hit(
        link_id=link.link_id,
        remote_ip=request.remote_addr,
        referer=request.referrer,
        user_agent=request.user_agent,
    )

    return redirect(link.outgoing_url)


@app.route(HomeURI.path, defaults={'path': ''}, methods=HomeURI.methods)
@app.route(DefaultURI.path, methods=DefaultURI.methods)
def frontend(path):
    return render_template('index.html')
