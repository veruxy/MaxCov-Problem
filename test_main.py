import maxcov
import transportation
import unittest

class TestOpeartions(unittest.TestCase):
    def test_maxcov(self):
        for i in range(1,4):
            in_file=f"graph{i}.in"
            platoons_in_file = f"platoons{i}.in"
            out_file=f"answ{i}.in"

            with open(out_file) as f:
                expected=float(f.readline())
            gr, w, n  = transportation.read_graph(in_file,False,0)
            platoon_paths, s, Tmax, source, dest = transportation.read_platoons(platoons_in_file)
            D = maxcov.FloydWarshall(n, w)

            DP, L = maxcov.Solve(gr, n, source, dest, Tmax,  w,D,platoon_paths, s)
            answer = DP[dest][Tmax]

            self.assertEqual(answer, expected)



if __name__ == "__main__":
    unittest.main()