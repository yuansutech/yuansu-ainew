module TreeOps where
import Data.List (foldl')
import qualified Data.Map as Map
data Tree a = Leaf | Node (Tree a) a (Tree a)
    deriving (Show, Eq)
insert :: Ord a => a -> Tree a -> Tree a
insert x Leaf = Node Leaf x Leaf
insert x (Node left value right)
    | x < value = Node (insert x left) value right
    | x > value = Node left value (insert x right)
    | otherwise = Node left value right
toList :: Tree a -> [a]
toList Leaf = []
toList (Node left value right) = toList left ++ [value] ++ toList right
treeHeight :: Tree a -> Int
treeHeight Leaf = 0
treeHeight (Node left _ right) = 1 + max (treeHeight left) (treeHeight right)
treeSize :: Tree a -> Int
treeSize Leaf = 0
treeSize (Node left _ right) = 1 + treeSize left + treeSize right
sumTree :: Num a => Tree a -> a
sumTree Leaf = 0
sumTree (Node left value right) = sumTree left + value + sumTree right
buildTree :: Ord a => [a] -> Tree a
buildTree = foldl' (flip insert) Leaf
wordFrequency :: String -> Map.Map String Int
wordFrequency text = Map.fromListWith (+) [(word, 1) | word <- words text]
main :: IO ()
main = do
    let tree = buildTree [5, 3, 8, 1, 4, 7, 9, 2, 6]
    print (toList tree)
    print (treeHeight tree)
    print (treeSize tree)
    print (sumTree tree)
    let freq = wordFrequency "the quick brown fox the lazy dog the"
    print (Map.toList freq)
    let empty = buildTree ([] :: [Int])
    print (treeHeight empty)
    let missing = Map.lookup "cat" freq
    print (missing + 1)
