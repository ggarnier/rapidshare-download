# Script para download automatico de arquivos do Rapidshare
# Autor: Guilherme Garnier - http://ggarnier.wordpress.com/
# Uso: rapidshare-download.py [-f <arquivo> / -u <url>]
#        -f <arquivo>: arquivo texto com lista de URLs para download
#        -u <url>: URL do Rapidshare para download

import urllib, urllib2, re, time, os, sys


def log(msg):
  print msg


def parse_post(page):
  download_url = ''
  dtime = ''
  try:
    # grep em page pra pegar as variaveis tt e c
    m = re.search(r'var tt = \'<form[^>]* action="([^"]*)"', page, re.DOTALL | re.IGNORECASE)
    download_url = m.group(1)
    m = re.search(r'var c=(\d+)', page, re.DOTALL | re.IGNORECASE)
    dtime = m.group(1)
  except: #AttributeError:
    # Verifica se ocorreu download limit
    try:
      m = re.search(r'Or try again in about (\d+) minute', page, re.DOTALL | re.IGNORECASE)
      dtime = m.group(1)
    except:
      # Verifica se o IP ja esta baixando um arquivo
      m = re.search(r'is already downloading a file', page, re.DOTALL | re.IGNORECASE)
      if m == None:
        log('Erro desconhecido')
        time.sleep(10)
        return False
      else:
        log('Voce ja esta baixando um arquivo. Aguardando 2 minutos para tentar novamente')
        time.sleep(120)
        return False

    # Aguarda o periodo informado mais um minuto
    log('Aguardando %s minutos' % dtime)
    time.sleep(60*(int(dtime)+1))
    return False

  # delay
  log('Delay de %s segundos' % dtime)
  time.sleep(int(dtime) + 2)

  # Retorna o link para download
  return download_url


def post_data(url):
  # post p/ pegar o link de download
  page = ''
  try:
    values = {'dl.start' : 'Free'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    page = response.read()
  except:
    log('Erro no post')
    time.sleep(10)
    return False

  return parse_post(page)


def download_file(url):
  # get da pagina inicial
  try:
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    page = response.read()
  except:
    log('Erro no get')
    time.sleep(10)
    return False

  # le o form
  try:
    m = re.search(r'<form id="ff" action="([^"]*)"', page, re.DOTALL | re.IGNORECASE)
    url = m.group(1)
  except: #AttributeError:
    log('Erro no get')
    return False

  # post p/ pegar o link de download - 3 tentativas
  download_url = False
  counter = 3
  while download_url == False and counter > 0:
    download_url = post_data(url)
    counter -= 1

  if download_url == False:
    log('Desistindo...')
    return False

  log('URL: %s' % download_url)
  counter = 3
  while counter > 0:
    ret = os.system('wget --tries=1 %s' % download_url)
    if ret == 0:
      log('Download com sucesso')
      return True

    counter -= 1

  log('Erro no download')
  return False


# Le os parametros de linha de comando
params = sys.argv
if (params.__len__() != 3 or (params[1] != '-f' and params[1] != '-u')):
  log('Uso: %s [-f <arquivo> / -u <url>]' % params[0])
  exit

if params[1] == '-f':
  for line in open(params[2], 'r').readlines():
    if line != '':
      log('Procurando %s' % line)
      if download_file(line) == False:
        download_file(line)
else:
  log('Procurando %s' % params[2])
  download_file(params[2])
