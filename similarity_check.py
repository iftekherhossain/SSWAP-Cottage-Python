import jellyfish
li = ['maxShift', 'distanceToLake', 'bookedBy', 'nearestCity', 'hasBedrooms', 'bookingStartDate', 'hasPlaces', 'bookingDuration', 'distanceToCity']
def ret_similar(match,li):
    maxi = 0
    for i,l in enumerate(li):
        temp_sim = jellyfish.jaro_similarity(match,l)
        if temp_sim>maxi:
            maxi = temp_sim
            out_idx = i
        
    return li[out_idx]
    
out = ret_similar("numDays",li)
print(out)