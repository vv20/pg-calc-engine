'''
Logic to run, end-to-end, the Pokemon team evaluation engine.
'''
from main.core.configuration import configure
from main.handler.distribute import handler as distribute_handler
from main.handler.enrich import handler as enrich_handler
from main.handler.evaluate import handler as evaluate_handler
from main.handler.reduce import handler as reduce_handler

if __name__ == '__main__':
    configure()
    enrich_handler()
    partitions = distribute_handler()
    for partition in partitions:
        evaluate_handler(event={'permutation': partition}, context={})
    reduce_handler()
