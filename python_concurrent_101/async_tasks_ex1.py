import asyncio
from codetiming import Timer
import logging
import queue


format = "%(asctime)s: %(message)s"
logging.basicConfig(
    format=format, level=logging.INFO, datefmt="%H:%M:%S")


class AsyncTask:
  def __init__(self, task_name: str, time_sec: int):
    self._name = task_name
    self._time_sec = time_sec

  @property
  def name(self):
    return self._name

  async def do(self):
    logging.info('Start task %s', self.name)
    await asyncio.sleep(self._time_sec)
    logging.info('End task %s', self.name)
    
    
cook_breakfast_task = AsyncTask('Cook breakfast', 2)
wash_clothes_task = AsyncTask('Wash clothes', 5)
do_house_chores_task = AsyncTask('Wash clothes', 3)
take_output_the_trash_task = AsyncTask('Wash clothes', 1)
all_async_tasks = [
    cook_breakfast_task,
    wash_clothes_task,
    do_house_chores_task,
    take_output_the_trash_task]


async def handle_tasks(task_queue, name):
  timer = Timer(text=f"Task {name} elapsed time: {{:.1f}}")
  while not task_queue.empty():
    try:
      task = task_queue.get()
    except:
      break
    timer.start()
    await task.do()
    timer.stop()

 
async def main():
  """
  This is the main entry point for the program
  """

  task_queue = queue.Queue()
  _ = [task_queue.put(task) for task in all_async_tasks]

  # Run the tasks
  with Timer(text="\nTotal elapsed time: {:.1f}"):
    await asyncio.gather(
        handle_tasks(task_queue, 'a1'),
        handle_tasks(task_queue, 'a2'),
        handle_tasks(task_queue, 'a3'),
    )


if __name__ == "__main__":
  asyncio.run(main())
