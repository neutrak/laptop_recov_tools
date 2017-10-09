#!/usr/bin/env python3

#a simple irc bot to allow remotely running shell commands
#(set to auto-run on guest accounts so I can track stolen computers)

#configuration
host="irc.foonetic.net"
port=6667
bot_nick="shellbot"
bot_user="1 2 3 4"
autojoin_channels=["#neurotoxin"]
#autojoin_channels=["#bot-test"]
#autojoin_channels=[]
authed_users=['neutrak','neutrak_','neutrak__','neutrak___','neutrak____']

buffer_size=1

import socket
import subprocess

#send a string to a socket in python3
#s is the socket
def py3send(s,message):
	s.send(message.encode('latin-1'))

#receive a string in python3
def py3recv(s,byte_count):
	data=s.recv(byte_count)
	return data.decode('utf-8')

def sock_writeln(s,text):
	print('>> '+text)
	py3send(s,text+"\n")

def sock_read(s):
	global buffer_size
	return py3recv(s,buffer_size)

#handle a command (after the user has been authorized)
def handle_botcmd(s,user,channel,cmd_str):
	global bot_nick
	
	print('got botcmd; cmd_str='+cmd_str)
	
	if(cmd_str.startswith('$')):
		cmd_str=cmd_str[1:]
		
		sock_writeln(s,'PRIVMSG '+channel+' :[ '+user+' @ '+channel+' ] $ '+cmd_str)
		
		#execute command, show output
		
		#limit output and running time
		runtime_limit=20
		output_lines=15
		
		#this a method of time-limiting which stackoverflow suggests
		#it depends on perl but other than that it seems fine
#		command=['perl','-e',"'alarm shift @ARGV; exec @ARGV'",str(runtime_limit)]
		
		#just use the unix-standard timeout command
		command=['timeout',str(runtime_limit)]
		command.extend(cmd_str.split(' '))
		
		print('>>$ '+(' '.join(command)))
		sub_proc=subprocess.Popen(' '.join(command),stderr=subprocess.STDOUT,stdout=subprocess.PIPE,shell=True)
		
		output,error=sub_proc.communicate()
		
		output=output.decode('utf-8')
		
		print('<result> '+output)
		
		result_lines=output.split("\n")
		line_count=len(result_lines)
		for line_idx in range(0,min(line_count,output_lines)):
			#ignore blank lines
			if(result_lines[line_idx]!=''):
				sock_writeln(s,'PRIVMSG '+channel+' :'+result_lines[line_idx])
		
		if(line_count>output_lines):
			sock_writeln(s,'PRIVMSG '+channel+' :<'+bot_nick+'> Warn: remaining output stripped due to irc limitations')
		
		if(output==''):
			sock_writeln(s,'PRIVMSG '+channel+' :<'+bot_nick+'> Warn: no output (command not found?)')
		

#read a line from the server and do what needs to be done as a result
def server_line(s,line):
	global autojoin_channels
	global bot_nick
	
	#debug
	print(line)
	
	#ignore blank lines
	if(line==''):
		return
	
	space_idx=line.find(' ')
	
	#no spaces is not valid IRC; ignore it
	if(space_idx<0):
		return
	
	#the command is everything before the first space
	cmd=line[0:space_idx]
	
	#if we got a ping, then send back a pong
	if(cmd.upper()=='PING'):
		reply='PONG'+line[space_idx:]
		sock_writeln(s,reply)
	#if the message started with a colon then it was probably a server message
	#in fact we're banking on it
	elif(cmd[0]==':'):
		cmd=line[space_idx+1:]
		
		#if the server says we're connected then join everything in the autojoin list
		if(cmd.startswith('001 ')):
			for channel in autojoin_channels:
				sock_writeln(s,"JOIN :"+channel)
		#if our nick was already in use then add a _ to the end
		elif(cmd.startswith('433 ')):
			bot_nick=bot_nick+'_'
			sock_writeln(s,'NICK '+bot_nick)
		elif(cmd.upper().startswith('PRIVMSG ')):
#			print('got a privmsg!')
			
			bang_idx=line[1:].find('!')
			if(bang_idx<0):
				return
			nick=line[1:bang_idx+1]
			
			msg=''
			channel=''
			
			fullmsg=line[space_idx+1:]
			space_idx=fullmsg.find(' ')
			if(space_idx>=0):
				fullmsg=fullmsg[space_idx+1:]
			
			space_idx=fullmsg.find(' ')
			if(space_idx>=0):
				channel=fullmsg[0:space_idx]
				fullmsg=fullmsg[space_idx+1:]
			
			colon_idx=fullmsg.find(':')
			if(colon_idx>=0):
				msg=fullmsg[colon_idx+1:]
			else:
				msg=fullmsg
			
			user_authed=False
			
			for authed in authed_users:
				if(authed.lower()==nick.lower()):
					user_authed=True
			
			print('user_authed for '+nick+' is '+('true' if True else 'false'))
			
			#for pms, pm back
			if(channel.lower()==bot_nick.lower()):
				channel=nick
			
			if(user_authed):
				handle_botcmd(s,nick,channel,msg)
			else:
				socket_writeln('PRIVMSG '+channel+' :user '+nick+' is not authorized to use this bot...')

#start the bot
def run_bot():
	global server
	global port
	global bot_nick
	global autojoin_channels
	
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))
	sock_writeln(s,'NICK :'+bot_nick)
	sock_writeln(s,'USER '+bot_user)
	
	data=''
	
	while(1):
		data+=sock_read(s)
		
		newline_idx=data.find("\n")
		if(newline_idx<0):
			continue
		
		line=data[0:newline_idx]
		if(line[len(line)-1]=="\r"):
			line=line[:-1]
		
		#reset data now that we have the first line out of it
		data=data[newline_idx+1:]
		
		server_line(s,line)
	

#runtime!
run_bot()

