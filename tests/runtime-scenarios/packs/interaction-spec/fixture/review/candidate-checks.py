from candidate import Window

w = Window()
assert w.fill() == [0, 1, 1, 1, 3, 3, 3, 0]
w.set_radius(0)
assert w.fill() == w.input
w.select(3)
assert w.render()['left']['selection'] == 3
w.set_mip(1)
assert w.render()['right']['mip'] == 1
print('4 checks passed')
