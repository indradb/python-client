function map(vertex)
    return arg
end

function reduce(first, second)
    first = first or 0.0
    return first + second
end

return { map=map, reduce=reduce }
