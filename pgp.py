#! /bin/env python

# Python Wrapper script for easy use of pgp 5.0i+

# Here is my pgp key, feel free to use it to test the module.
# ( Make sure to send me your public key... )

author_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: PGPfreeware 5.0i for non-commercial use

mQCNAzrJfyoAAAEEAOy0l2T7yehz3HJhkVSeKLiabyoHg9VaMXe+WPHsTFWjBJ6b
leo63X2/1ze4xXCc9gEpqjMsW3JJBf7gCbXh4ajZ9vPdJiJx+ekoXVjmfg9e0yvD
eEBhIg0ksm3PH+K7aQR5IJ1S/d0GxF+2rL7Sgb539yBC3I2kz6GNIOJ8nvFLAAUR
tCFNYXR0aGV3IFNjaGluY2tlbCA8bWF0dEBudWxsLm5ldD6JAJUDBRA6yX8qoY0g
4nye8UsBAYG+BAC+ji8Kzk5hh3oGoCU2BNj8hR8V/4Kr7KgScDrYPYmd+V95qBwj
uAxOFc6tE8tnBzqC3jVoa8UBy+NK0pojgaIHqN+KAF8iDVrnW6ghiPIBVvcPgh5m
mzUG1nWGZ08FiUSaDPsQTIle5431LOccDaP19H8vuaWoPLvn/umMGAHWTQ==
=ZdcB
-----END PGP PUBLIC KEY BLOCK-----
"""

import os, sys, string, rfc822

# Basic Functions - encrypt, decrypt, sign, verify

def encrypt(data, userid):
	"Encrypt a string to all keys matching 'userid'."
	pw,pr = os.popen2('pgpe -fast -r "'+userid+'"')
	pw.write(data)
	pw.close()
	ctext = pr.read()
	return ctext

def decrypt(data):
	"Decrypt a string - if you have the right key."
	pw,pr = os.popen2('pgpv -f')
	pw.write(data)
	pw.close()
	ptext = pr.read()
	return ptext

def sign(data, userid=None):
	"Sign some text, using the option private key matching <userid>."
	if userid <> None:
		pw,pr = os.popen2('pgps -u "'+userid+'"')
	else:
		pw,pr = os.popen2('pgps')
	pw.write(data)
	pw.close()
	stext = pr.read()
	return stext

def verify(data):
	"Verify that a message came from a sender."
	# What should this return?
	return decrypt(data)

# Encrypt for multiple keys.

def encrypt_for_many(data, userid_list):
	"Encrypt a string for multiple <userid> keys."
	userid = ''
	for user in userid_list:
		userid = userid + ' -r "' + user + '"'
	stdin, stdout = os.popen2('pgpe -fast '+userid)
	stdin.write(data)
	stdin.close()
	ctext = stdout.read()
	return ctext

# Key Management functions.  Incomplete.

def extract_key(userid):
	"Get the ascii representation of a public key."
	stdout = os.popen('pgpk -x '+userid)
	return stdout.read()

def get_key_list(userid = None):
	"Get a list of keys on your keychain matching <userid>."
	if userid == None:
		stdout = os.popen('pgpk -l')
	else:
		stdout = os.popen('pgpk -l '+userid)
	data = stdout.readlines()
	keys = []
	for line in data:
		if line[:4] == 'uid ':
			keys.append(line[5:-1])
	return keys

def keys(userid = None): # Convenience
	"Return a list of [<userid1>, <userid2>]."
	return get_key_list(userid)

def remove_key(userid):
	print "Not yet implemented."
	pass

def add_key(text):
	#stdin, stdout = os.popen2('pgpk -a
	# Need to be able to add a key from stdin, or use a temp file...
	print "Not yet implemented."
	pass
	
# Complex Functions - ie (en/de)crypting email messages, etc.

def decrypt_email(filename):
	"""Check to see if a file is an encoded rfc822 Message,
and decode it if it is, and you have a key."""
	try:
		fp = open(filename, 'r+')
	except IOError, name:
		print "File Not Found:", name
		sys.exit()
	m = rfc822.Message(fp)
	text = fp.read()
	if text[:27] == '-----BEGIN PGP MESSAGE-----':
		plaintext = decrypt(text)
		m.rewindbody()
		fp.write(plaintext)
		fp.truncate()
	fp.close()

def encrypt_email(filename):
	"""Encrypt a valid rfc822 Message, if and only if all recipients
have a public key on your keyring."""
	try:
		fp = open(filename, 'r+')
	except IOError, name:
		print "File Not Found:", name
		sys.exit()
	m = rfc822.Message(fp)
	text = fp.read()
	userid_list = m.getaddrlist('to')
	for item in m.getaddrlist('cc'):
		userid_list.append(item)
	for item in m.getaddrlist('bcc'):
		userid_list.append(item)		
	try:
		addrlist = []
		for userid in userid_list:
			test = os.popen('pgpk -l "'+userid[1]+'"').readlines()
			if test[-1][0] == '0':                   # Maybe make handle multiple keys?
				print "Cannot Encrypt! Not one key for user. (maybe more)"
	 			#sys.exit()
	 			raise KeyError
	 		else:
	 			addrlist.append(userid[1])
		ciphertext = encrypt_for_many(text,addrlist)
		m.rewindbody()
		fp.write(ciphertext)
		fp.truncate()
	except KeyError:
		ciphertext = text
		fp.close()
	# BeOS Only - Should possibly be in the MailDaemon Addon.
	if sys.platform[:4] == 'beos':
		try:
			import bedbm
			db = bedbm.open(filename)
			db['MAIL:status']="Pending"
			db['MAIL:content_length'] = len(ciphertext)
			db.close()
		except ImportError: # No bedbm - use basic commands instead.
			command1 = 'addattr MAIL:status Pending "'+filename+'"'
			command2 = 'addattr -t int MAIL:content_length '+str(len(ciphertext))+' "'+filename+'"'
			os.system(command1)
			os.system(command2)
	

	
if __name__ == '__main__':
	"Test stuff."
	fp = open('.profile')
	data = fp.read()
	#print data
	text = encrypt(data, "matt@null.net")
	#print text
