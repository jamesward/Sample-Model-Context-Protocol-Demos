import {Schema} from "effect";

export const EmployeeSchema = Schema.Struct({
  name: Schema.String,
  skills: Schema.Array(Schema.String)
})

type Employee = typeof EmployeeSchema.Type

const firstNames = [
  "James", "Mary", "John", "Patricia", "Robert",
  "Jennifer", "Michael", "Linda", "William", "Elizabeth"
];

const lastNames = [
  "Smith", "Johnson", "Williams", "Brown", "Jones",
  "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
];

const skills = [
  "Kotlin", "Java", "Python", "JavaScript", "TypeScript",
  "React", "Angular", "Spring Boot", "AWS", "Docker",
  "Kubernetes", "SQL", "MongoDB", "Git", "CI/CD",
  "Machine Learning", "DevOps", "Node.js", "REST API", "GraphQL"
];

function getRandomElement<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

function getRandomElements<T>(array: T[], min: number, max: number): T[] {
  const count = Math.floor(Math.random() * (max - min + 1)) + min;
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

// Generate 100 unique employees
const generateEmployees = (): Employee[] => {
  const employees: Employee[] = [];
  const usedNames = new Set<string>();

  while (employees.length < 100) {
    const firstName = getRandomElement(firstNames);
    const lastName = getRandomElement(lastNames);
    const fullName = `${firstName} ${lastName}`;

    if (!usedNames.has(fullName)) {
      usedNames.add(fullName);
      employees.push({
        name: fullName,
        skills: getRandomElements(skills, 2, 5)
      });
    }
  }

  return employees;
};

export const employees: Employee[] = generateEmployees();
