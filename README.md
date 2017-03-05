__Info__

This python library created for driving Swalle bluetooth robotic ball


__Requirements__

Go through the setup for bluez and [bluepy](https://github.com/IanHarvey/bluepy), and run the bluepy test program to make sure it works. (This step can be a bit of a pain). Make sure the bluepy files are somewhere python can see.


__Example__

```python
ball = Ball(name='SW21T025766')

ball.white()
time.sleep(1)
ball.red()
time.sleep(1)
ball.green()
time.sleep(1)
ball.blue()
time.sleep(1)

ball.white()
ball.lights()
time.sleep(1)

ball.forward()
time.sleep(1)
ball.left()
time.sleep(1)
ball.right()
time.sleep(1)
ball.back()
time.sleep(1)
