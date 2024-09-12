import os

# handlers
METODOS = [
        '/start -> %s'%( 'mensaje de bienvenida' ),
        '/ayuda -> %s'%( 'mensaje de ayuda' ),
        '/estado -> %s'%( 'último estado del check' ),
        '/buscar-> %s'%( 'buscar apuntes' ),
        '/contactar -> %s'%( 'contactar con Emi' ),
        '/contribuir -> %s'%( 'invitar a Emi a un café jaja' ),
	' ---------- MEDIDAS --------- ',
        '/temp -> %s'%( 'temperatura de la habitación' ),
	'/tCPU -> %s'%( 'temperatura de la CPU' ),
        '/pron -> %s'%( 'pronóstico del tiempo' ),
        '       /pron hoy | mañana | pmañana',
	' ---------- SISTEMA --------- ',
	'/apagar -> %s'%( 'apagar el bot' ),
	'/ipLocal -> %s'%( 'decir ip local del host' ),
        '/renov -> %s'%( 'última renovación de libros' )
    ]

# botones
FOO = { '/buscar' : 0 ,
        '/contactar' : 1 ,
        '/contribuir' : 2,
        '/ayuda' : 3,
        '/start' : 5
        }

CHROMEDRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"

FECHA_PATH = os.path.join( os.path.abspath('.') , 'config/fecha.txt' )
TIME_INTERVAL_RENOVADOR = 43200

LOGS_PATH = os.path.join( os.path.abspath('.') , 'config/logs.txt' )

TIME_INTERVAL_ENVIAR_TIEMPO = 43200
