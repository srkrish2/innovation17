import cherrypy
import mongodb_controller as mc
PREVIOUS_URL_KEY = "previous_url"
USERNAME_KEY = "username"


class NewAccountHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        username = data['username']
        email = data['email']
        password = data['password']

        result = {
            "success": False
        }
        if "@" not in email:
            result["issue"] = "Illegal email"
            print "Illegal email"
            return result
        if mc.is_email_in_use(email):
            result["issue"] = "Email already in use"
            print "Email already in use"
            return result
        if mc.is_username_taken(username):
            result["issue"] = "This username is already taken"
            print "This username is already taken"
            return result

        # encrypt the password
        # password_hash = sha256_crypt.encrypt(password)

        mc.new_account(username, email, password)  # password_hash)
        result["success"] = True
        cherrypy.session[USERNAME_KEY] = username
        if PREVIOUS_URL_KEY in cherrypy.session:
            result["url"] = cherrypy.session[PREVIOUS_URL_KEY]
            cherrypy.session.pop(PREVIOUS_URL_KEY)
        else:
            result["url"] = "index"
        return result


class SignInHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        name = data['name']
        password = data['password']

        is_email = '@' in name
        success = False
        if is_email:
            if mc.is_email_in_use(name):
                hashed_password = mc.get_password_for_email(name)
                if password == hashed_password:
                    # if sha256_crypt.verify(password, hashed_password):
                    success = True
                    name = mc.get_username_from_email(name)
        elif mc.is_username_taken(name):
            hashed_password = mc.get_password_for_username(name)
            if password == hashed_password:
                # if sha256_crypt.verify(password, hashed_password):
                success = True
        result = {}
        if not success:
            result["success"] = False
            result["url"] = "index"
            return result
        else:
            result["success"] = True
            cherrypy.session[USERNAME_KEY] = name
            if PREVIOUS_URL_KEY in cherrypy.session:
                result["url"] = cherrypy.session[PREVIOUS_URL_KEY]
                cherrypy.session.pop(PREVIOUS_URL_KEY)
            else:
                result["url"] = "index"
            return result
