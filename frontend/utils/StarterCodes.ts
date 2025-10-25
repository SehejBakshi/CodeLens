export type Language = 'javascript' | 'python' | 'cpp' | 'java' | 'typescript' | 'csharp';

export const Languages = [
  { label: "JavaScript", value: "javascript" },
  { label: "Python", value: "python" },
  { label: "C++", value: "cpp" },
  { label: "Java", value: "java" },
  { label: "TypeScript", value: "typescript" },
  { label: "C#", value: "csharp" },
];

export const StarterCodes = {
  javascript: `// JavaScript starter code
function hello() {
  console.log("Hello, world!");
}
hello();`,
  python: `# Python starter code
def hello():
    print("Hello, world!")

hello()`,
  cpp: `// C++ starter code
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, world!" << endl;
    return 0;
}`,
  java: `// Java starter code
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
    }
}`,
  typescript: `// TypeScript starter code
function hello(): void {
    console.log("Hello, world!");
}
hello();`,
  csharp: `// C# starter code
using System;

class Program {
    static void Main() {
        Console.WriteLine("Hello, world!");
    }
}`
};
