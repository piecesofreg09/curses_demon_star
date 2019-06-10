class test:
    x = 1
    def __init__(self, y):
        self.y = y
    
    def change_x(self, x):
        self.x = x
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
        
test1 = test(1)
print(test1.get_x())
print(test1.x)
print(test1.change_x(2))
print(test1.get_x())

print(test1.get_y())

