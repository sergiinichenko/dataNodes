import numpy as np

class ConcaveHull(object):  
    _points = []
    points  = None
    concave_hull = []

    def __init__(self):
        self._points = None
        self.concave_hull = []

    def __call__(self, point_set):
        self._points = point_set
        self.points  = None
        return self.compute_hull()
    

    def get_orientation(self, origin, p1, p2):
        '''
        Returns the orientation of the Point p1 with regards to Point p2 using origin.
        Negative if p1 is clockwise of p2.
        :param p1:
        :param p2:
        :return: integer
        '''
        difference = (
            ((p2[0] - origin[0]) * (p1[1] - origin[1]))
           -((p1[0] - origin[0]) * (p2[1] - origin[1]))
        )

        return difference

    def compute_hull(self):
        '''
        Computes the points that make up the convex hull.
        :return:
        '''
        self.points = self._points

        # get leftmost point
        self.points = self.points[np.lexsort(np.transpose(self.points)[::-1])]  # sort the data by x-axis, then by y-axis
        start  = self.points[0]

        self.concave_hull.append(start)
        self._findhull(start)

        return self.concave_hull

    def _findhull(self, point):
        if self.points is None:
            return None
        
        distance = 0.0
        C, index = None, None
        for i, point in enumerate(self.points):
            current_dis = abs(self.compute_distance(P, Q, point))
            if current_dis > distance: # find a point whose distance from PQ is the maximum among all the points
                C = point
                index = i
                distance = current_dis
        if C is not None:
            self.concave_hull.append(C)
            points = np.delete(points, index, axis=0) #delete C from original points
        else:
            try:
                raise Exception("The input points are located on the same line. No convex hull is found!")
            except Exception as inst:
                print(type(inst))
                print(inst.args) 
                return
            

        S1, S2 = self.triangle_partition(points, P, C, Q) #interate this process for S1 and S2
        self._findhull(S1, P, C)
        self._findhull(S2, C, Q)


    def get_k_nearest(self, ix, k):
        """
        Calculates the k nearest point indices to the point indexed by ix
        :param ix: Index of the starting point
        :param k: Number of neighbors to consider
        :return: Array of indices into the data set array
        """
        ixs = self.indices

        base_indices = np.arange(len(ixs))[ixs]
        distances = self.haversine_distance(self.data_set[ix, :], self.data_set[ixs, :])
        sorted_indices = np.argsort(distances)

        kk = min(k, len(sorted_indices))
        k_nearest = sorted_indices[range(kk)]
        return base_indices[k_nearest]

    def haversine_distance(self, loc_ini, loc_end):
        lon1, lat1, lon2, lat2 = map(np.radians,
                                     [loc_ini[0], loc_ini[1],
                                      loc_end[:, 0], loc_end[:, 1]])

        delta_lon = lon2 - lon1
        delta_lat = lat2 - lat1

        a = np.square(np.sin(delta_lat / 2.0)) + \
            np.cos(lat1) * np.cos(lat2) * np.square(np.sin(delta_lon / 2.0))

        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
        meters = 6371000.0 * c
        return meters


        """
        Calculates the convex hull of the data set as an array of points
        :param k: Number of nearest neighbors
        :return: Array of points (N, 2) with the concave hull of the data set
        """
        if self.data_set.shape[0] < 3:
            return None

        if self.data_set.shape[0] == 3:
            return self.data_set

        # Make sure that k neighbors can be found
        kk = min(k, self.data_set.shape[0])

        first_point = self.get_lowest_latitude_index(self.data_set)
        current_point = first_point

        # Note that hull and test_hull are matrices (N, 2)
        hull = np.reshape(np.array(self.data_set[first_point, :]), (1, 2))
        test_hull = hull

        # Remove the first point
        self.indices[first_point] = False

        prev_angle = 270    # Initial reference id due west. North is zero, measured clockwise.
        step = 2
        stop = 2 + kk

        while ((current_point != first_point) or (step == 2)) and len(self.indices[self.indices]) > 0:
            if step == stop:
                self.indices[first_point] = True

            knn = self.get_k_nearest(current_point, kk)

            # Calculates the headings between first_point and the knn points
            # Returns angles in the same indexing sequence as in knn
            angles = self.calculate_headings(current_point, knn, prev_angle)

            # Calculate the candidate indexes (largest angles first)
            candidates = np.argsort(-angles)

            i = 0
            invalid_hull = True

            while invalid_hull and i < len(candidates):
                candidate = candidates[i]

                # Create a test hull to check if there are any self-intersections
                next_point = np.reshape(self.data_set[knn[candidate]], (1,2))
                test_hull = np.append(hull, next_point, axis=0)

                line = asLineString(test_hull)
                invalid_hull = not line.is_simple
                i += 1

            if invalid_hull:
                return self.recurse_calculate()

            # prev_angle = self.calculate_headings(current_point, np.array([knn[candidate]]))
            prev_angle = self.calculate_headings(knn[candidate], np.array([current_point]))
            current_point = knn[candidate]
            hull = test_hull

            # write_line_string(hull)

            self.indices[current_point] = False
            step += 1

        poly = asPolygon(hull)

        count = 0
        total = self.data_set.shape[0]
        for ix in range(total):
            pt = asPoint(self.data_set[ix, :])
            if poly.intersects(pt) or pt.within(poly):
                count += 1
            else:
                d = poly.distance(pt)
                if d < 1e-5:
                    count += 1

        if count == total:
            return hull
        else:
            return self.recurse_calculate()















class ConvexHull2D:
    '''
    This function returns an 2D numpy array containing the locations of points which 
    can form a convex hull for 2D point clouds using quick hull. 
    Pls refer to README for detailed discription for quick hull
    Sample Usage:
        #Initilization
        convex_hull_creator = ConvexHull2D()
        #find the convex hull
        points = np.random.random((100,2)) 
        hull = convex_hull_creator(points)
        #plot
        plt.plot(hull[:,0], hull[:,1])
        plt.show()
    '''
    def __init__(self):
        self.points = None
        self.convext_hull = []

    def __call__(self, point_set):
        return self.forward(point_set)

    def divide_area(self, start, end, points):
        '''
        Input Arguments:
            start: The start point of the boundary line
            end: The end point of the boundary line
            points: The points data to be divided
        
        Output Arguments:
            S1: points that on the right side area by drawing a line from the start to the end
            S2: points that on the left side area by drawing a line from the start to the end
        Function: 
            Divide the point set into two sets by comparing the cross product
        '''

        if points is None or points.shape[0] < 1:
            return None, None
        S1, S2 = [], []
        for _, point in enumerate(points):
            dis =  self.compute_distance(start, end, point)
            if dis > 0:
                S1.append(point)
            else:
                S2.append(point)
        S1 = np.vstack(S1) if len(S1) else None
        S2 = np.vstack(S2) if len(S2) else None
        return S1, S2


    def triangle_partition(self, points, P, C, Q):
        '''
        Input Arguments:
            P, Q, C: vertices to form a triangle
            points: an array of points to be divided into partitions
        
        Output Arguments:
            S1: points on the right side of vector PC
            S2: points on the right side of vector CQ
    
        Function: 
            Divide the point set into two sets into the following region:
                        C
                        *
                S_2   * *  S_1
                    *   *
                    *     *
                Q   * * * * *  P 
        '''
        if points is None:
            return None, None
        S1, S2 = [], []
        for _, point in enumerate(points):
            disPC = self.compute_distance(P, C, point) #Use cross product to determine which side the point is on
            disCQ = self.compute_distance(C, Q, point)
            if disPC > 0 and disCQ < 0:
                S1.append(point)
            elif disPC < 0 and disCQ > 0:
                S2.append(point)
        S1 = np.vstack(S1) if len(S1) else None
        S2 = np.vstack(S2) if len(S2) else None
        return S1, S2    
        
    def compute_distance(self, start, end, point, eps=1e-8):
        '''
        Return the cross product from point to segment defined by (start, end)
        '''
        return np.cross(end-start,point-start)/(np.linalg.norm(end-start)+eps) #prevent from dividing by 0

    def clock_sort(self, x):
        '''
        Return sorted vertices in the clockwise using the angle 
        between the x-axis and vector pointing from the center to the point
        '''
        x0, y0 = x[:,0].mean(), x[:,1].mean()
        theta = np.arctan2(x[:,1] - y0, x[:,0] - x0)
        index = np.argsort(theta)
        x = x[index]
        
        return x


    def reset(self):
        self.points = None
        self.convext_hull = []

    def forward(self, point_set):
        if point_set is None or len(point_set) < 3:
            print("No valid convex hull is found! Please provide more than 3 unique points")
            return point_set
        self.reset()          
        self.points = np.unique(point_set, axis=0) #get rid of duplicate elements
        return self._quickhull()
    
    def isInside(self, points):
        if len(self.convext_hull) == 0:
            print("Please build a convex hull first.")
            return None
        result = []   
        for point in points:
            result.append(self._isInside(point))
        return np.asarray(result)

    def _quickhull(self):        
        self.points = self.points[np.lexsort(np.transpose(self.points)[::-1])]  # sort the data by x-axis, then by y-axis
        left_most, right_most = self.points[0], self.points[-1]     #find the left-most point and right-most point
        self.points = self.points[1:-1]     #Get the rest points
        self.convext_hull.append(left_most)     #add the left-most point into the output
        self.convext_hull.append(right_most)    #add the right-most point into the output

        self.right_points, self.left_points = self.divide_area(start=left_most, 
                                                          end=right_most, 
                                                          points=self.points)

        self._findhull(self.right_points, left_most, right_most)
        self._findhull(self.left_points, right_most, left_most)

        self.convext_hull = np.stack(self.convext_hull)
        self.convext_hull = self.clock_sort(self.convext_hull)
        #if self.convext_hull.shape[0] < 3:
        #    try:
        #        raise Exception("Not enough points are found for convex hull. Please check your input and other information")
        #    except Exception as inst:
        #        print(type(inst))
        #        print(inst.args) 
        #else:                   
        return self.convext_hull

    def _findhull(self, points, P, Q):
        if points is None:
            return None
        distance = 0.0
        C, index = None, None
        for i, point in enumerate(points):
            current_dis = abs(self.compute_distance(P, Q, point))
            if current_dis > distance: # find a point whose distance from PQ is the maximum among all the points
                C = point
                index = i
                distance = current_dis
        if C is not None:
            self.convext_hull.append(C)
            points = np.delete(points, index, axis=0) #delete C from original points
        else:
            try:
                raise Exception("The input points are located on the same line. No convex hull is found!")
            except Exception as inst:
                print(type(inst))
                print(inst.args) 
                return
            

        S1, S2 = self.triangle_partition(points, P, C, Q) #interate this process for S1 and S2
        self._findhull(S1, P, C)
        self._findhull(S2, C, Q)
    
    def _isInside(self, point):
        for i in range(self.convext_hull.shape[0]-1):
            start, end = self.convext_hull[i], self.convext_hull[i+1]
            if self.compute_distance(start, end, point) < 0:
                return False
        return True
    
