#!/usr/bin/python
import sys
import os

# NAME: split
# IN: string
# OUT: array de los difonos que componen el string de entrada. Si el string presenta
# un signo de interrogacion se inserta como ultimo elemento del array.

def split(string):
  pregunta = 0
  if string[-1] == "?":
    pregunta = 1
    string = string[:len(string)-1]
  s = "x"
  for i in range(0,len(string)):
    s = s + string[i]*2
  s = s + "x"
  array = [s[i:i+2] for i in range(0, len(s), 2)]
  if pregunta:
    array.append("?") 
  return array

# NAME: gen_script
# IN: array de difonos, output
# OUT: praat script en ../difonos/script.praat
# La funcion toma un array de difonos a combinar y crea un script
# en Praat que los combina y guarda el wav resultante
# en el output tomado como parametro.

def gen_script(array, output):
  text_file = open("../difonos/script.praat", "w")
  s = ""
  i = 1
  for difono in array:
    s = s + 'Read from file: "' + difono + '.wav"\n'
    s = s + 'Rename: "' + str(i) + '"\n'
    i = i + 1
  s = s + '\n'
  for i in range(1,len(array)+1):
    if i == 1:
      s = s + 'selectObject: "Sound ' + str(i) + '"\n'
    else:
      s = s + 'plusObject: "Sound ' + str(i) + '"\n'
  s = s + "Concatenate recoverably\n\n" + \
          'selectObject: "Sound chain"\n' + \
          'Save as WAV file: "'
  if output[0] == "/":
    s = s + output + '"'
  else:
    s = s + '../src/' + output + '"'
  text_file.write(s)

# NAME: read_pitch_tier
# OUT: PitchTier
# La funcion abre el archivo "12345.PitchTier", examina los
# campos xmin, xmax, y los atributos "number" y "value" de
# cada punto y los almacena en una clase llamada Pitchier
# que se encuentra declarada debajo de este comentario.

class PitchTier:
  def __init__(self):
    self.values = {}
    self.xmin = ""
    self.xmax = ""

def read_pitch_tier():
  text_file = open("12345.PitchTier", "r")
  lines = text_file.readlines()
  pitch = PitchTier()
  for line in lines:
    value = 0
    if "xmin" in line:
      l = line.split()
      pitch.xmin = float(l[-1])
    if "xmax" in line:
      l = line.split()
      pitch.xmax = float(l[-1])
    if "number" in line:
      l = line.split()
      number = float(l[-1])
    if "value" in line:
      l = line.split()
      value = float(l[-1])
      pitch.values[number] = value
  return pitch

# NAME: save_modified_pitch_tier
# IN: PitchTier
# OUT: "12345.PitchTier"
# La funcion crea un archivo "12345.PitchTier" en base a los atributos
# del objeto PitchTier pasado como parametro. 

def save_modified_pitch_tier(pitch):
  s = 'File type = "ooTextFile"\n' + \
      'Object class = "PitchTier"\n\n' + \
      'xmin = ' + str(pitch.xmin) + ' \n' + \
      'xmax = ' + str(pitch.xmax) + ' \n' + \
      'points: size = ' + str(len(pitch.values)) + ' \n'
  i = 0
  for key, value in sorted(pitch.values.items()):
    s = s + 'points [' + str(i+1) + ']:\n' + \
            '    number = ' + str(key) + ' \n' + \
            '    value = ' + str(value) + ' \n'
    i = i + 1 
  file = open("12345.PitchTier", "w")
  file.write(s)

# NAME: inicializar_puntos
# IN: PitchTier
# OUT: array de puntos
# La funcion toma el objeto PitchTier de entrada y calcula la cantidad
# de puntos que tiene cada silaba del texto a sintetizar. Para ello
# toma en cuenta la duracion total de los difonos que componen el texto
# y se fija en que silaba se encuentra cada punto.

def inicializar_puntos(pitch):
  puntos_por_silaba = []
  n = len(texto)
  silabas = n/2
  silaba_t = pitch.xmax/float(silabas)
  silaba_actual = 0
  cont = 0
  for key, value in sorted(pitch.values.items()):
    silaba_anterior = silaba_actual
    silaba_actual = int(key/silaba_t)
    if (silaba_anterior != silaba_actual):
      puntos_por_silaba.append(cont)
      cont = 1
    else:
      cont = cont + 1
  puntos_por_silaba.append(cont)
  return puntos_por_silaba

# NAME: func
# IN: a,b,c
# OUT: int
# La funcion calcula f=a*b^2+c

def func(a, b, c):
  return a*b**2+c

# NAME: change_pitch_tier
# IN: PitchTier
# OUT: PitchTier
# La funcion modifica el objeto PitchTier de entrada y lo retorna. Para
# mas informacion, leer el README que se encuentra en este directorio.  

def change_pitch_tier(pitch, texto):
  n = len(texto)
  silabas = n/2
  silaba_t = pitch.xmax/float(silabas)
  puntos_por_silaba = inicializar_puntos(pitch)
 
  silaba_actual = 0
  punto = 0
  for key, value in sorted(pitch.values.items()):

    if silabas == 1:
      if texto[n-1] == 'A':
        a = 85.0/(puntos_por_silaba[0]**2)
      else:
        a = 35.0/(puntos_por_silaba[0]**2)
      f = a * punto**2 + 115
      pitch.values[key] = f
      punto = punto + 1

    else:
      silaba_anterior = silaba_actual
      silaba_actual = int(key/silaba_t)
      if (silabas%2 == 1 and silaba_actual != 0) or silabas%2 == 0:
      
        if (silaba_anterior != silaba_actual):
          punto = 0

# Seteamos la prosodia final separando en 4 casos posibles, segun las vocales:

        punto = punto + 1

        if ((silabas%2 == 1 and silaba_actual%2 == 1) or (silabas%2 == 0 and silaba_actual%2 == 0)):

          if texto[2*silaba_actual+1] == 'A' and texto[2*(silaba_actual+1)+1] == 'A':
            a = 85.0/(puntos_por_silaba[silaba_actual]**2)
            a1 = 85.0/(puntos_por_silaba[silaba_actual+1]**2)
            c = 110
            pitch.values[key] = func(a,punto,c)
            empezar_por_final = 0

          if texto[2*silaba_actual+1] == 'a' and texto[2*(silaba_actual+1)+1] == 'A':
            a1 = 85.0/(puntos_por_silaba[silaba_actual+1]**2)
            c = 115
            empezar_por_final = 0

          if texto[2*silaba_actual+1] == 'A' and texto[2*(silaba_actual+1)+1] == 'a':
            a = 85.0/(puntos_por_silaba[silaba_actual]**2)
            c = 110
            a1 = 85.0/(puntos_por_silaba[silaba_actual+1]**2)
            empezar_por_final = 1
            pitch.values[key] = func(a,punto,c)

          if texto[2*silaba_actual+1] == 'a' and texto[2*(silaba_actual+1)+1] == 'a':
            a = 35.0/(puntos_por_silaba[silaba_actual]**2)
            c = 110
            a1 = 35.0/(puntos_por_silaba[silaba_actual+1]**2)
            empezar_por_final = 1
            pitch.values[key] = func(a,punto,c)

        else:
          if empezar_por_final:
            pitch.values[key] = func(a1, puntos_por_silaba[silaba_actual]-punto, c)
          else:
            pitch.values[key] = func(a1,punto,c)

  return pitch

# NAME: add_prosodia
# IN: output y texto
# OUT: wav file
# La funcion toma el output y texto del wav sintetizado. Extrae el PitchTrack
# con un script de Praat, lo modifica y finalmente lo reemplaza con otro
# script de Praat. El resultado es un wav con la prosodia modificada.

def add_prosodia(output, texto):
  os.system("./../praat extraer-pitch-track.praat " + output + " 12345.PitchTier 50 300")
  pitch_tier = read_pitch_tier()
  pitch_tier = change_pitch_tier(pitch_tier, texto)
  save_modified_pitch_tier(pitch_tier)
  os.system("./../praat reemplazar-pitch-track.praat " + output + " 12345.PitchTier " + output + " 50 300")

if __name__ == '__main__':

  texto = sys.argv[1]

# El output deberia ser pasado como parametro.

  output = sys.argv[2]

# Obtenemos los difonos del texto.

  difonos = split(texto)

# Verificamos si el texto es una pregunta o no.

  pregunta = 0
  if difonos[-1] == "?":
    pregunta = 1
    difonos.pop()

  gen_script(difonos, output)

# Combinamos los difonos del texto con el
# script  de Praat recien creado.

  os.system('./../praat ../difonos/script.praat')

# Agregamos la prosodia en caso de tratarse de una pregunta.

  if pregunta:
    add_prosodia(output, texto[:len(texto)-1])
    os.system('rm 12345.PitchTier')

  os.system('rm ../difonos/script.praat')
