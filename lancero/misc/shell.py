#!/usr/bin/env python
#coding: utf-8
#from: http://www.python.org.br/wiki/PythonNoLugarDeShellScript

"""
Receita: Python no lugar de Shell Script

Apresentado originalmente como palestra relâmpago na PyConBrasil 2008

Por JoaoBueno

Há vários motivos para se usar um script shell em vez de um script python, as vezes.

No entanto, às vezes, há mais motivos ainda para se usar um script Python no lugar
de um script shell e o único motivo pelo qual não fazemos isso é por que tem que
ser feitas algumas chamadas a comandos externos, e termos que escrever " os.system("comando [parametros"]) " em vez de simplesmente "comando [parâmetros]"

Seus problemas acabaram!!!!

Uam implementeação microscópica de um factory em python permtie que você use construções do tipo

Esconder número das linhas

   1 sh.ls()
   2 sh.ps("aux")
   3 sh.iptables("-t nat -L")

em vez de suas contrapartes embrulhadas em os.system (ou popen)

E tudo o que voce tem que fazer é incorporar

Esconder número das linhas

import os

class Cmd(object):
   def __init__(self, cmd):
       self.cmd = cmd
   def __call__(self, *args):
       return os.system("%s %s" % (self.cmd, " ".join(args)))

class Sh(object):
    def __getattr__(self, attribute):
        return Cmd(attribute)

sh = Sh()

ao seu código. Depois disso os exemplos acima funcionarão. (seu script ficará ainda mais compacto e legível se você colocar essas classes utilitárias num módulo separado)

Explicando a mágica: a classe "Sh" - da qual não precisa haver mais de uma instância, reescreve o método que recupera atributos da classe. Ao tentar achar um atributo de um objeto dessa classe, o método getattr é chamado, com o nome do atributo como parâmetro.

Em um objeto normal, o valor do atributo é procurado no dicionario interno da classe.
Mas é possível criar atributos dinamicamente. No caso, se a idéia fosse simplesmente
executar um comando externo sem parâmetro algum, a classe já poderia retornar somente
os.system(atributo) - e nesse caso, simplesmente "sh.ls" já executaria o comando
externo "ls".

Mas queremos ir além e passar parâmetros. Então o nosso getattr não faz a chamada ao processo externo. Em vez disso ele cria dinamicamente um objeto da classe "cmd" que pode ser chamado - como qualquer objeto em python cuja classe defina o método "call". Esse objeto tem como atributo, em sua criação, o nome do comando externo.

O python então recupera um objeto executável no getattr e como esse objeto é seguido de parênteses - que é a sintaxe para execução do objeto, a função call do mesmo é chamada.

Exemplo: o interpretador encontra
Esconder número das linhas

   1 sh.ps("aux")

Então ele sabe que vai precisar fazer uma chamada ao atributo "ps" do objeto "sh". Ele primerio precisa obter o objeto "ps" - - faz então a chamada ao getattr, que por sua vez, cria uma nova instâncuia da classe Cmd, que registra que seu atributo cmd é "ps". Com esse objeto cmd em mãos, o python faz a chamada ao mesmo, o que executa o método call. Esse por sua vez, chama o processo externo, concatenando o nome do executável e os parâmetros, e retorna o valor de retorno de os.system

Uma alternativa usando Subprocess

Por HenriqueBaggio

Atente que o os.system no exemplo anterior é muito bonito para você ver a execução no terminal interativo. Agora, o seguinte exemplo usa a classe Popen do módulo subprocess, que possui mais recursos para manipulação de processos. Com ela, podemos obter de uma forma muito simples as saídas padrão e de erro (stdout e stderr) do programa que queremos executar. Se essa saída for textual, há grandes chances de que você possa processar essa saída sem chamar nenhum outro comando externo - enquanto que um shell script exigiria chamadas a processos awk, cut ou grep para separar os valores interessantes.

Veja como fica essa alternativa:

Esconder número das linhas

   1 from subprocess import Popen, PIPE
   2 
   3 class Cmd(object):
   4    def __init__(self, cmd):
   5        self.cmd = cmd
   6    def __call__(self, *args):
   7        command = '%s %s' %(self.cmd, ' '.join(args))
   8        result = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
   9        return result.communicate()
  10 
  11 class Sh(object):
  12     def __getattr__(self, attribute):
  13         return Cmd(attribute)

As mudanças estão apenas na função "call", que agora faz uso da classe "Popen". O que fizemos nesse exemplo foi direcionar as saídas padrão e de erro do comando chamado de forma que o método "communicate" retorne uma tuple (stdoutdata, stderrdata), que podemos facilmente manipular depois, conforme nossa necessidade.

Outro recurso interessante para o nosso shell seria obter os códigos de erro que o processo chamado eventualmente gerasse. Para isso usa-se o método "Popen.returncode", que retorna um inteiro que representa o erro de acordo com a tabela de erros do sistema operacional.
"""

import os

class SystemCmd(object):
   def __init__(self, cmd):
       self.cmd = cmd
   def __call__(self, *args):
       return os.system("%s %s" % (self.cmd, " ".join(args)))

class SystemSh(object):
    def __getattr__(self, attribute):
        return SystemCmd(attribute)

#sh = SystemSh()


from subprocess import Popen, PIPE

class PopenCmd(object):
   def __init__(self, cmd):
       self.cmd = cmd
   def __call__(self, *args):
       command = '%s %s' %(self.cmd, ' '.join(args))
       result = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
       return result.communicate()

class PopenSh(object):
    def __getattr__(self, attribute):
        return PopenCmd(attribute)

#sh = PopenSh()

class InteractiveCmd(object):
   def __init__(self, cmd):
       self.cmd = cmd
   def __call__(self, *args):
       command = '%s %s' %(self.cmd, ' '.join(args))
       result = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
       communication = result.communicate()
       print(communication[0])
       
       return communication


class Sh(object):
    def __getattr__(self, attribute):
        return InteractiveCmd(attribute)

#sh = Sh()
