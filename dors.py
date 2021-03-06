import random
import time
from datetime import datetime

alpha = 0.1

class dummyDs(object):
    def __init__(self):
        pass

    def insert_key(self, key):
        pass

    def remove_key(self, key):
        pass

    def create_ds(self, points):
        return dummyDs()

    def factory(self, arg):
        return dummyDs()

class Node(object):
    def __init__(self, key, left, right, next_dim_ds=None):
        # self.alpha = alpha
        self.key = key
        self.size = 1
        self.size += left.size if left is not None else 0
        self.size += right.size if right is not None else 0
        self.left = left
        self.right = right
        if next_dim_ds is None:
            if len(self.key.coords) > 1:
                next_dim_ds = Node(self.key.child(), None, None)
            else:
                next_dim_ds = dummyDs()
        self.next_dim_ds = next_dim_ds
        # print("i am %s and my next is %s" % (key, next_dim_ds))

    def insert_key(self, key):
        # print("hi i'm %s, and %s is being inserted. current state follows" % (self.key, key))
        # print("%s" % self)

        if self.size > 1:
            # print "branch 1"
            # check balance
            left = self.left.size if self.left is not None else 0
            right = self.right.size if self.right is not None else 0
            if key >= self.key:
                right += 1
            else:
                left += 1
            if left < alpha*self.size or right < alpha*self.size:
                # print "need to rebalance"
                # need to rebalance
                n = self.create_ds(self.enumerate(key), self.next_dim_ds)
                self.key = n.key
                self.left = n.left
                self.right = n.right
                self.size = n.size
                self.next_dim_ds = n.next_dim_ds
                return

        # actually insert the key
        self.size += 1
        # print("i am %s" % self.key)
        self.next_dim_ds.insert_key(key.child())
        # if self.key is None:
        if key >= self.key:
            # print "bigger than me"
            if self.right is None:
                self.right = Node(key, None, None, self.next_dim_ds.factory([key.child()]))
            else:
                self.right.insert_key(key)
        else:
            # print "smaller than me"
            if self.left is None:
                self.left = Node(key, None, None, self.next_dim_ds.factory([key.child()]))
            else:
                self.left.insert_key(key)

    def remove_key(self, key):
        # print self
        if self.size >= 2:
            # check balance
            left = self.left.size if self.left is not None else 0
            right = self.right.size if self.right is not None else 0
            if key >= self.key:
                right -= 1
            else:
                left -= 1
            if left < alpha*self.size or right < alpha*self.size:
                # need to rebalance
                n = self.create_ds(self.remove_enumerate(key), self.next_dim_ds)
                self.key = n.key
                self.left = n.left
                self.right = n.right
                self.size = n.size
                self.next_dim_ds = n.next_dim_ds
                return

        # actually remove the key
        self.size -= 1
        self.next_dim_ds.remove_key(key.child())
        if key == self.key:
            n = self.create_ds(self.remove_enumerate(key))
            self.key = n.key
            self.left = n.left
            self.right = n.right
            self.size = n.size
            self.next_dim_ds = n.next_dim_ds
        elif key > self.key:
            if self.right is None:
                print("key does not exist")
                # throw an error
            else:
                self.right.remove_key(key)
        else:
            if self.left is None:
                print("key does not exist")
                # throw an error
            else:
                self.left.remove_key(key)

    def rangeQuery(self, rawMin, rawMax, toReturn=None):
        minCoords = [min(rawMin.coords[i], rawMax.coords[i]) for i in range(len(rawMin.coords))]
        pointMin = Point(minCoords)
        maxCoords = [max(rawMin.coords[i], rawMax.coords[i]) for i in range(len(rawMin.coords))]
        pointMax = Point(maxCoords)
        # print("pmin is %s" % pointMin)
        # print("pmax is %s" % pointMax)
        # print("i am %s and my next ds is %s" % (self.key, self.next_dim_ds))
        if self.key > pointMax:
            if self.left is not None:
                return self.left.rangeQuery(pointMin, pointMax)
            else:
                return []
        elif self.key < pointMin:
            if self.right is not None:
                return self.right.rangeQuery(pointMin, pointMax)
            else:
                return []
        else:
            # print("got to split")
            toReturn = []
            if self.left is not None:
                self.left.searchLeft(pointMin, pointMax, toReturn)

            if self.key >= pointMin and self.key <= pointMax:
                toReturn.append(self.key)

            if self.right is not None:
                self.right.searchRight(pointMin, pointMax, toReturn)
            return toReturn

    def searchLeft(self, pointMin, pointMax, toReturn):
        if self.left is None and self.right is None:
            if self.key <= pointMax and self.key >= pointMin:
                toReturn.append(self.key)
        else:
            if self.key >= pointMin:
                if self.left is not None:
                    self.left.searchLeft(pointMin, pointMax, toReturn)

                if self.key >= pointMin and self.key <= pointMax:
                    toReturn.append(self.key)

                if self.right is not None:
                    if len(self.key.coords) == 1:
                        toReturn.extend(self.right.enumerate())
                    else:
                        toReturn.extend(self.right.next_dim_ds.rangeQuery(pointMin.child(), pointMax.child(), toReturn))
            else:
                if self.right is not None:
                    self.right.searchLeft(pointMin, pointMax, toReturn)


    def searchRight(self, pointMin, pointMax, toReturn):
        if self.left is None and self.right is None:
            if self.key >= pointMin and self.key <= pointMax:
                toReturn.append(self.key)
        else:
            if self.key <= pointMax:
                if self.left is not None:
                    if len(self.key.coords) == 1:
                        toReturn.extend(self.left.enumerate())
                    else:
                        toReturn.extend(self.left.next_dim_ds.rangeQuery(pointMin.child(), pointMax.child(), toReturn))
                
                if self.key <= pointMax and self.key >= pointMin:
                    toReturn.append(self.key)

                if self.right is not None:
                    self.right.searchRight(pointMin, pointMax, toReturn)
            else:
                if self.left is not None:
                    self.left.searchRight(pointMin, pointMax, toReturn)


    def enumerate(self, newKey=None):
        to_return = []
        if self.left is not None:
            if newKey is not None and newKey < self.key:
                to_return = self.left.enumerate(newKey)
            else:
                to_return = self.left.enumerate(None)
        elif newKey is not None and newKey < self.key:
            to_return = [newKey]

        to_return.append(self.key)

        if self.right is not None:
            if newKey is not None and newKey >= self.key:
                to_return.extend(self.right.enumerate(newKey))
            else:
                to_return.extend(self.right.enumerate(None))
        elif newKey is not None and newKey >= self.key:
            to_return.append(newKey)
        return to_return

    def remove_enumerate(self, delKey=None):
        to_return = []
        if self.left is not None:
            if delKey is not None and delKey < self.key:
                to_return = self.left.remove_enumerate(delKey)
            else:
                to_return = self.left.remove_enumerate(None)

        if self.key != delKey:
            to_return.append(self.key)
            
        if self.right is not None:
            if delKey is not None and delKey > self.key:
                to_return.extend(self.right.remove_enumerate(delKey))
            else:
                to_return.extend(self.right.remove_enumerate(None))
        return to_return

    def create_ds(self, points, next_dim_ds=None):
        # print("i am making a ds, and my points follow")
        # for point in points:
        #     print point
        # print("i am done")

        if next_dim_ds is not None:
            next_dim_ds.create_ds([point.child() for point in points])
        if len(points) == 1:
            return Node(points[0], None, None)
        elif len(points) == 2:
            left = Node(points[0], None, None)
            return Node(points[1], left, None)
        else:
            # print(points[0:len(points)/2])
            left = self.create_ds(points[0:len(points)/2])
            right = self.create_ds(points[len(points)/2 + 1:])
            return Node(points[len(points)/2], left, right, next_dim_ds)


    def factory(self, points):
        return self.create_ds(points)

    def __str__(self):
        return self.tostr()

    def tostr(self, level=0):
        ret = "  "*level + str(self.key) + "\n"
        if self.left is None and self.right is None:
            return ret
        if self.right is not None:
            ret += self.right.tostr(level + 1)
        else:
            ret += "  "*(level+1) + "None\n"
        if self.left is not None:
            ret += self.left.tostr(level + 1)
        else:
            ret += "  "*(level+1) + "None\n"
        return ret

class Point(object):
    def __init__(self, coords, root=None):
        self.coords = coords
        if root is None:
            root = self
        self.root = root

    def __eq__(self, other):
        if other is None:
            return False
        return self.coords == other.coords

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if other is None:
            print self
        if self.coords[0] == other.coords[0]:
            return self.child() < other.child()
        return self.coords[0] < other.coords[0]

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return self == other or self > other

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        s = [str(c) for c in self.coords]
        return '(' + ','.join(s) + ')'

    def child(self):
        if len(self.coords) > 1:
            return Point(self.coords[1:], self.root)
        else:
            return None

class Tester(object):
    def __init__(self):
        pass

    def runAllTests(self):
        self.points = [Point([key]) for key in [1, 5, 10, 11, 12, 13]]
        print("running tests")
        # self.testCreateTree()
        # self.testInsert()
        # self.testRemove()
        # self.testRangeQuery()
        # self.test2DRangeQuery()
        # self.test3DRangeQuery()
        self.benchmark3DRangeQuery(10, 1)
        # self.manual_testing()
        print("all tests succeeded")

    @staticmethod
    def sameSortedList(expected, returned):
        assert(len(expected) == len(returned))
        for i in range(len(expected)):
            assert(expected[i] == returned[i])
        return True

    def testCreateTree(self):
        # note: depracated
        t = Node.create_ds(self.points)
        assert(Tester.sameSortedList(self.points, t.enumerate()))

    def testInsert(self):
        # note: depracated
        t = Node.create_ds(self.points)
        t.insert_key(Point([2]))
        t.insert_key(Point([50]))
        assert(Tester.sameSortedList([Point([key]) for key in [1, 2, 5, 10, 11, 12, 13, 50]], t.enumerate()))

    def testRemove(self):
        # note: depracated
        t = Node.create_ds(self.points)
        t.insert_key(Point([2]))
        t.insert_key(Point([50]))
        assert(Tester.sameSortedList([Point([key]) for key in [1, 2, 5, 10, 11, 12, 13, 50]], t.enumerate()))
        t.remove_key(Point([1]))
        t.remove_key(Point([10]))
        t.remove_key(Point([50]))
        assert(Tester.sameSortedList([Point([key]) for key in [2, 5, 11, 12, 13]], t.enumerate()))

    def testRangeQuery(self):
        # note: depracated
        t = Node.create_ds(self.points)
        assert(Tester.sameSortedList([Point([key]) for key in [5, 10, 11]], t.rangeQuery(Point([5]), Point([11]))))
        assert(Tester.sameSortedList([], t.rangeQuery(Point([6]), Point([8]))))
        assert(Tester.sameSortedList(self.points, t.rangeQuery(Point([0]), Point([20]))))

    def test2DRangeQuery(self):
        points = [Point(key) for key in [[0,0], [1,7], [3,3], [5,5], [6, 2]]]
        derp = Node(Point([0]), None, None)
        t = derp.create_ds(points, Node(Point([0]), None, None))
        # t = Node(Point([0]), None, None).create_ds(points, Node(Point([0]), None, None))
        points = t.rangeQuery(Point([0,8]), Point([1,0]))
        for point in points:
            print point

    def test3DRangeQuery(self):
        # points = [Point(key) for key in [[0,0,0], [5,5,5], [0,7,7], [7,0,0], [12,12,0], [0,8,0]]]
        # derp = Node(Point([0]), None, None)
        # t = derp.create_ds(points, Node(Point([0,0]), None, None, Node(Point([0]), None, None)))
        t = Node(Point([0,0,0]), None, None) # inside range
        t.insert_key(Point([5,5,5])) # inside range
        t.insert_key(Point([50,50,50])) # outside range
        t.insert_key(Point([2, 50, 50])) # outside range on dims 2 and 3
        t.insert_key(Point([2,2,2])) # inside range (but later removed)
        t.insert_key(Point([2, 7, 8])) # inside range
        t.insert_key(Point([-5, 4, 3])) # outside range
        t.remove_key(Point([2,2,2]))
        returned_points = t.rangeQuery(Point([0,0,0]), Point([20,10,20]))
        for point in returned_points:
            print point
            # print point.root

        assert(Tester.sameSortedList(returned_points, [Point([0,0,0]), Point([2,7,8]), Point([5,5,5])]))

        # note to self: just need to figure out the exact conditions of this recursion and creation of next-ds

    def benchmark3DRangeQuery(self, n, k):
        maxDim = n 
        t = Node(Point([0,0,0]), None, None)
        for i in range(n):
            newPoint = Point([random.randint(0,maxDim), random.randint(0,maxDim), random.randint(0,maxDim)])
            # print("inserting %s" % newPoint)
            t.insert_key(newPoint)
            # print(t)

        queryPairs = []

        for j in range(k):
            queryPairs.append([Point([random.randint(0,maxDim), random.randint(0,maxDim), random.randint(0,maxDim)]),
                Point([random.randint(0,maxDim), random.randint(0,maxDim), random.randint(0,maxDim)])])
        
        print "starting benchmarking run"
        # dt = datetime.now()
        tt = time.time()

        for j in range(k):
            t.rangeQuery(queryPairs[j][0], queryPairs[j][1])

        # dt2 = datetime.now()
        # print dt2.microsecond - dt.microsecond
        print time.time() - tt

    def manual_testing(self):
        t = Node(Point([0,0,0]), None, None)
        t.insert_key(Point([3,5,9]))
        t.insert_key(Point([5,10,12]))
        t.insert_key(Point([0,7,2]))
        print(t)




t = Tester()
t.benchmark3DRangeQuery(1000, 10000)

