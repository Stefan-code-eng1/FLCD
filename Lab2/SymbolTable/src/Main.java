import Pair.Pair;
import SymTable.SymbolTable;

public class Main {
    public static void main(String[] args) {
        SymbolTable table = new SymbolTable(10);
        table.add("a");
        table.add("b");
        System.out.println(table);

        System.out.println(table.containsTerm("a"));
        System.out.println(table.containsTerm("cd"));

        System.out.println(table.findPositionOfTerm("a"));
        System.out.println(table.findPositionOfTerm("d"));

        Pair<Integer,Integer> pos = new Pair<>(7,0);

        System.out.println(table.findByPos(pos));

        System.out.println(table.getSize());
    }
}