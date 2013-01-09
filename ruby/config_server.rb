require 'rubygems'
require 'redis'
require 'sinatra'

APPCONFIG = "appconfig:env:"
APPINDEX = "appconfig:index"

#
# .env and .ini dynamic configurator
# .env is suitable to foreman, .ini is the goodole ini file
#  section.test, 1
#  section.elmo, 2

# conf/ini file:
# [section]
# test = 1
# elmo = 2

# env file
# section.test=1
# section.elmo=2


conn = Redis.new


get '/ini/:appname' do
  appname = params['appname']
  s = conn.sismember APPINDEX, appname
  halt 404, "Application not found" unless s

  h = conn.hgetall APPCONFIG + appname
  halt 401, "Application has no configuration" if h == nil

  options = Hash.new{|h, k| h[k] = []}

  h.keys.each do |k| 
    l = k.split '.'
    if l.length == 2 then
        options[l[0]] << [l[1], h[k]]
    else
        options['_'] << [l[0], h[k]]
    end
  end
  
  buffer = ""

  options.keys.each do |option| 
    buffer += "[#{option}]\n" unless option == '_'
      options[option].each do |a| 
        buffer += "#{a[0]}=#{a[1]}\n"
      end
    end

  buffer
end

get '/env/:appname' do
  appname = params['appname']
  s = conn.sismember(APPINDEX, appname)
  halt 404, "Application not found" unless s
  
  h = conn.hgetall APPCONFIG + appname
  halt 401, "Application has no configuration" if h == nil
  
  buffer = ""
  h.each do |k,v|
    buffer += "#{k}=#{v}\n"
  end

  buffer
end

post '/env/:appname' do
  appname = params['appname']
  key = params['key']
  val = params['val']
  
  s = conn.sismember APPINDEX, appname
  halt 404, "Application not found" unless s

  h = conn.hgetall APPCONFIG + appname
  halt 401, "Application has no configuration" if h == nil
  
  conn.hset(APPCONFIG + appname, key, val)
end

post '/app/new' do
    appname = params['appname']
    s = conn.sismember(APPINDEX, appname)
    abort 401, "Application already exists" if s
    conn.sadd(APPINDEX, appname)
end

post '/app/delete' do
    appname = params['appname']
    s = conn.sismember(APPINDEX, appname)
    abort 401, "Application not found" if s == False
    conn.srem(APPINDEX, appname)
    conn.delete(APPCONFIG + appname)
end
