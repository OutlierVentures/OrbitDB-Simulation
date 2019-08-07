


#
# // Shuffle randomize elements of neighbors
# func Shuffle(slice []int) {
# 	r := rand.New(rand.NewSource(time.Now().Unix()))
# 	for len(slice) > 0 {
# 		n := len(slice)
# 		randIndex := r.Intn(n)
# 		slice[n-1], slice[randIndex] = slice[randIndex], slice[n-1]
# 		slice = slice[:n-1]
# 	}
# }

#
# func MergerBloomClock(bc1 []byte, bc2 []byte) []byte {
# 	var ret []byte
# 	for i := 0; i < len(bc1); i++ {
# 		if bc1[i] <= bc2[i] {
# 			ret = append(ret, bc2[i])
# 		} else if bc1[i] > bc2[i] {
# 			ret = append(ret, bc1[i])
# 		}
# 	}
# 	return ret
# }
#
# func SubtractSlice(nodes, broadcast []string) []string {
# 	var ret []string
# 	for _, v := range nodes {
# 		if !in(v, broadcast) {
# 			ret = append(ret, v)
# 		}
# 	}
# 	return ret
# }
#
# func in(element string, nodes []string) bool {
# 	for _, v := range nodes {
# 		if v == element {
# 			return true
# 		}
# 	}
# 	return false
# }
#
# func Intersection(s1, s2 []string) string {
# 	for i := range s2 {
# 		if in(s2[i], s1) {
# 			return s2[i]
# 		}
# 	}
# 	return ""
# }