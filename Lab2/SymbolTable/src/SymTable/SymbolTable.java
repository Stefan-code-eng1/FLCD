package SymTable;
import HashTable.HashTable;
import Pair.Pair;

public class SymbolTable {

    private Integer size;
    private final HashTable hashTable;


    public SymbolTable(Integer size){
        hashTable = new HashTable(size);
    }

    public String findByPos(Pair<Integer,Integer> pos){
        return hashTable.findByPos(pos);
    }

    public HashTable getHashTable(){
        return hashTable;
    }

    public Integer getSize(){
        return hashTable.getSize();
    }

    public Pair<Integer, Integer> findPositionOfTerm(String term){
        return hashTable.findPositionOfTerm(term);
    }

    public boolean containsTerm(String term){
        return hashTable.containsTerm(term);
    }

    public boolean add(String term){
        return hashTable.add(term);
    }

    @Override
    public String toString(){
        return this.hashTable.toString();
    }

}
