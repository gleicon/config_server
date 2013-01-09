require 'rubygems'                                                                                                                                                                
require 'sinatra'                                                               
set :env,  :production                                                          
disable :run                                                                    
                                                                                
require './config_server'                                                                 
                                                                                
run Sinatra::Application
