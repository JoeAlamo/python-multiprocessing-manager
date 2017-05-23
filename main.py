import mp_example.manager
import mp_example.worker


def main():
    # Create our consumer manager, instruct it to manage 10 workers with the target action of create_worker
    manager = mp_example.manager.ConsumerManager(10, mp_example.worker.create_worker)
    # Boot up and enter management loop
    manager.run()

if __name__ == '__main__':
    main()
