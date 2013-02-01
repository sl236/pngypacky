#!/usr/bin/python
import os
import sys
import stat
import zlib
import base64
import struct

# ---------------------------------------------------------------------------------------
args = sys.argv[1:]
if( len( args ) < 0 ):
	print >> sys.stderr, """Usage: pngypacky.py directory-or-file directory-or-file...
  *  .js files explicitly listed on the command line will be eval()ed on load, 
     in the order in which they are mentioned on the command line. 
  *  All files will be provided as base64 encoded data: URIs in the PackedFiles 
     global array, indexed by their path. 
  *  A DecodeFile global function is also defined; it will return 
	 the decoded payload of a base64 encoded data: URI
"""
	sys.exit( 0 )

# ---------------------------------------------------------------------------------------
# See http://daeken.com/superpacking-js-demos for an overview of the process

# ---------------------------------------------------------------------------------------

def adddir( path ):
	encoded = ''
	files = os.listdir( path )
	for file in files:
		fpath = path+'/'+file
		mode = os.stat( fpath ).st_mode
		if stat.S_ISDIR(mode):
			encoded += adddir( fpath )
		elif stat.S_ISREG( mode ):
			encoded += addfile( fpath )
		else:
			print >> sys.stderr, 'not sure how to deal with ' + fpath + ', skipping'
	return encoded

def addfile( path ):
	encoded = ''
	mimetype = 'text/plain'
	if( item.lower().endswith('.png') ):
		mimetype = 'image/png'
	elif( item.lower().endswith('.jpg') ):
		mimetype = 'image/jpeg'
	elif( item.lower().endswith('.jpeg') ):
		mimetype = 'image/jpeg'
	elif( item.lower().endswith('.gif') ):
		mimetype = 'image/gif'
	elif( item.lower().endswith('.css') ):
		mimetype = 'text/css'
	elif( item.lower().endswith('.html') ):
		mimetype = 'text/html'
	elif( item.lower().endswith('.js') ):
		mimetype = 'application/javascript'
	with open( path, 'rb' ) as fd:
		encoded = 'PackedFiles["' + path + '"]="data:'+mimetype+';base64,' + base64.b64encode( fd.read() ) + '";'+"\n"
	print >> sys.stderr, 'added: ' + path + '(' + mimetype + ')'
	return encoded	

# ---------------------------------------------------------------------------------------

payload = "var PackedFiles=[];function DecodeFile(b,l,c,S,B,X,p,r,i){r='';b=b.replace((/^.+,/),r);X=b.length;l=b.indexOf('=');l=0|(((X*6)+7)/8)-((l>-1)?X-l:0);S=String.fromCharCode;B=[[65,91],[97,123],[48,58],[43,44],[47,48]];X=0;c=[];for(p in B){for(i=B[p][0];i<B[p][1];i++){c[S(i)]=X++}}B=X=p=i=0;for(;i<l;i++){for(;X<8;X+=6,B=(B<<6)|c[b[p++]]);r+=S((B>>>(X-=8))&0xFF)}return r}"

# ---------------------------------------------------------------------------------------

postfix = ''

for item in args:
		mode = os.stat( item ).st_mode
		if stat.S_ISDIR(mode):
			payload += adddir( item )
		elif stat.S_ISREG( mode ):
			payload += addfile( item )
			if( item.lower().endswith('.js') ):
				postfix += 'eval(DecodeFile(PackedFiles["'+item+'"]));'
		else:
			print >> sys.stderr, 'not sure how to deal with ' + item + ', skipping'

payload = b'\x00' + payload + postfix + b'\x00'

# ---------------------------------------------------------------------------------------
width = 1024
height = int((len(payload)+(width-1))/width)
# bootstrap = "<img onload=with(document.createElement('canvas'))p=width="+repr(width)+",(c=getContext('2d')).drawImage(this,e='',0);d=c.getImageData(0,0,p,1).data;while(p)e+=String.fromCharCode(d[p-=4]);(1,eval)(e) src=#>"
bootstrap  = "<canvas id=c>"
bootstrap += "<img onload=for(w=c.width="+repr(width)+",h=c.height="+repr(height)+","
bootstrap += "a=c.getContext('2d'),a.drawImage(this,p=0,0),e='',S=String.fromCharCode,d=a.getImageData(0,0,w,h).data;t=d[p+=4];)"
bootstrap += "e+=S(t);(1,eval)(e) src=#>"

def pngchunk( type, data ):
	return struct.pack('!I', len(data)) + type + data + struct.pack('!I', (zlib.crc32( type + data ) & 0xffffffff) )

data  = b'\x89PNG\x0D\x0A\x1A\x0A'
data += pngchunk( 'IHDR', struct.pack('!IIBI', width, height, 8, 0 ) )
data += pngchunk( 'boot', bootstrap )

pos = 0
result = ''
while( pos < len(payload) ):
    result += b'\x00' + payload[pos:pos+width]
    pos += width
payload = zlib.compress(result.ljust((width+1)*height, b'\x00'))
data += pngchunk( 'IDAT', payload )
sys.stdout.write( data )

print >> sys.stderr, "bootstrap: " + repr(len(bootstrap))
print >> sys.stderr, "payload: " + repr(len(payload))
print >> sys.stderr, "headers: " + repr(len(data)-(len(bootstrap)+len(payload)))
print >> sys.stderr, "TOTAL: " + repr(len(data))
