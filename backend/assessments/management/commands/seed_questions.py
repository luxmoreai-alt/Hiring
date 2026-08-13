import random
from django.core.management.base import BaseCommand
from django.core.management import call_command
from assessments.models import Question


APTITUDE = {
    "quantitative": [
        ("A product marked ₹800 is sold at a 10% discount. What is the selling price?", ["₹680", "₹700", "₹720", "₹740"], 2),
        ("The ratio of two numbers is 3:5 and their sum is 64. What is the larger number?", ["24", "32", "40", "48"], 2),
        ("A train travels 180 km in 3 hours. What is its average speed?", ["50 km/h", "55 km/h", "60 km/h", "65 km/h"], 2),
        ("What is 25% of 360?", ["80", "90", "100", "120"], 1),
        ("The average of 12, 18, 24, 30 and 36 is:", ["22", "24", "26", "28"], 1),
        ("Simple interest on ₹5,000 at 8% per annum for 2 years is:", ["₹600", "₹700", "₹800", "₹900"], 2),
        ("If 8 workers finish a job in 15 days, how many days will 12 workers take at the same rate?", ["8", "10", "12", "14"], 1),
        ("A number increased by 20% becomes 144. What was the original number?", ["110", "115", "120", "125"], 2),
        ("What is the HCF of 36 and 48?", ["6", "8", "12", "16"], 2),
        ("A bag has 3 red and 2 blue balls. Probability of drawing a red ball is:", ["2/5", "3/5", "1/2", "3/4"], 1),
        ("Solve: 3x + 7 = 28.", ["5", "6", "7", "8"], 2),
        ("A rectangle is 12 cm long and 7 cm wide. Its area is:", ["38 cm²", "72 cm²", "84 cm²", "96 cm²"], 2),
        ("A shopkeeper gains 15% on an item costing ₹400. The selling price is:", ["₹440", "₹450", "₹460", "₹475"], 2),
        ("Two numbers are in ratio 4:7. If the smaller is 28, the larger is:", ["42", "45", "49", "56"], 2),
        ("A can complete work in 12 days and B in 18 days. Their one-day combined work is:", ["5/36", "1/15", "1/30", "7/36"], 0),
    ],
    "logical": [
        ("Find the next number: 2, 6, 12, 20, 30, ?", ["36", "40", "42", "44"], 2),
        ("All roses are flowers. Some flowers fade quickly. Which conclusion is certain?", ["All roses fade quickly", "Some roses fade quickly", "Roses are flowers", "No roses fade"], 2),
        ("If SOUTH is coded as TPVUI, how is NORTH coded using the same rule?", ["OPSUI", "OPSTI", "NPSUI", "OQTUI"], 0),
        ("A is taller than B. B is taller than C. Who is shortest?", ["A", "B", "C", "Cannot determine"], 2),
        ("Odd one out: 16, 25, 36, 49, 63", ["16", "36", "49", "63"], 3),
        ("If today is Wednesday, what day will it be after 45 days?", ["Friday", "Saturday", "Sunday", "Monday"], 1),
        ("Complete the series: AZ, BY, CX, ?", ["DV", "DW", "DX", "EV"], 1),
        ("Ravi faces north, turns right, then right again. Which direction is he facing?", ["North", "South", "East", "West"], 1),
        ("Book is to Reading as Fork is to:", ["Drawing", "Eating", "Writing", "Cooking"], 1),
        ("Five people stand in a line. P is before Q, Q before R. Which must be true?", ["R is before P", "P is before R", "Q is last", "P is first"], 1),
        ("Find the missing term: 81, 27, 9, 3, ?", ["0", "1", "2", "1/3"], 1),
        ("If CAT = 24 by adding alphabet positions, DOG = ?", ["24", "25", "26", "27"], 2),
        ("Statements: No pens are pencils. Some pencils are red. Which follows?", ["Some red things are not pens", "All red things are pens", "No red thing is a pen", "Some pens are red"], 0),
        ("Arrange logically: 1.Seed 2.Fruit 3.Plant 4.Flower", ["1,3,4,2", "1,4,3,2", "3,1,4,2", "1,3,2,4"], 0),
        ("In a code, 5 means '+', 7 means '×'. What is 4 7 3 5 2?", ["14", "16", "18", "20"], 0),
    ],
    "verbal": [
        ("Choose the synonym of 'meticulous'.", ["Careless", "Precise", "Rapid", "Ordinary"], 1),
        ("Choose the antonym of 'scarce'.", ["Rare", "Limited", "Abundant", "Small"], 2),
        ("Fill in the blank: Neither the manager nor the employees ___ aware of the change.", ["was", "were", "is", "has"], 1),
        ("Choose the correctly spelled word.", ["Accomodation", "Accommodation", "Acommodation", "Accommadation"], 1),
        ("Identify the error: She has been working here since five years.", ["She has", "been working", "here", "since five years"], 3),
        ("One word for a person who speaks many languages:", ["Linguist", "Polyglot", "Orator", "Lexicographer"], 1),
        ("Complete the analogy: Bird : Aviary :: Lion : ?", ["Den", "Cage", "Zoo", "Lair"], 0),
        ("Choose the passive voice of: 'The team completed the project.'", ["The project completed the team", "The project was completed by the team", "The team was completed by the project", "The project is completed"], 1),
        ("The idiom 'hit the nail on the head' means:", ["Make a mistake", "State exactly what is right", "Work very hard", "Cause an injury"], 1),
        ("Choose the correct sentence.", ["He don't know", "He doesn't knows", "He doesn't know", "He not knows"], 2),
        ("Rearrange into a sentence: P: for success Q: consistent effort R: is essential", ["PQR", "QRP", "RPQ", "RQP"], 1),
        ("Choose the meaning of 'pragmatic'.", ["Idealistic", "Practical", "Careless", "Uncertain"], 1),
        ("Fill in the blank: The report is divided ___ three sections.", ["between", "among", "into", "by"], 2),
        ("Which word is a noun?", ["Beautiful", "Beauty", "Beautify", "Beautifully"], 1),
        ("Choose the indirect form: He said, 'I am busy.'", ["He said that I am busy", "He said that he was busy", "He says he is busy", "He told he was busy"], 1),
    ],
    "non-verbal": [
        ("Which symbol comes next? ○, △, ○○, △△, ○○○, ?", ["△△", "△△△", "○○○○", "△△△△"], 1),
        ("A square is rotated 90° clockwise twice. Its total rotation is:", ["90°", "180°", "270°", "360°"], 1),
        ("Complete the pattern: ■ □ ■ □ ■ ?", ["■", "□", "▲", "○"], 1),
        ("Which does not belong?", ["Triangle", "Square", "Circle", "Cube"], 3),
        ("A mirror is placed to the right of 'b'. Which lowercase letter shape is closest to its image?", ["b", "d", "p", "q"], 1),
        ("Count the sides in two separate triangles and one square.", ["7", "8", "9", "10"], 3),
        ("Complete: ↑, →, ↓, ?", ["↑", "←", "↗", "→"], 1),
        ("A paper is folded once in half and one hole is punched through it. On unfolding, holes visible:", ["1", "2", "3", "4"], 1),
        ("Which shape has rotational symmetry of order 4?", ["Non-square rectangle", "Equilateral triangle", "Square", "Semicircle"], 2),
        ("Pattern: 1 dot, 3 dots, 5 dots, ?", ["6 dots", "7 dots", "8 dots", "9 dots"], 1),
        ("If ▲ becomes ▼ after a transformation, the operation is best described as:", ["Colour change", "Vertical reflection", "Scaling", "Translation"], 1),
        ("Which 2D shape can form a cone when rotated around one straight side?", ["Rectangle", "Right triangle", "Circle", "Square"], 1),
        ("Complete the alternation: ●■, ■●, ●■, ?", ["●●", "■■", "■●", "●■"], 2),
        ("A cube has how many edges?", ["6", "8", "10", "12"], 3),
        ("Which view of a cylinder appears circular?", ["Front", "Side", "Top", "Diagonal only"], 2),
    ],
}

TECH = {
    "mern-stack-developer": [
        ("Which data structure uses FIFO order?", "Queue", ["Stack", "Tree", "Heap"]), ("Binary search on a sorted array runs in:", "O(log n)", ["O(n)", "O(n²)", "O(1)"]),
        ("Encapsulation primarily means:", "Bundling data and methods with controlled access", ["Copying objects", "Running code in parallel", "Sorting data"]), ("Which SQL clause filters grouped results?", "HAVING", ["WHERE", "ORDER BY", "JOIN"]),
        ("A process waiting for a resource held by another in a cycle is:", "Deadlock", ["Paging", "Starvation only", "Caching"]), ("Git command that creates a new branch and switches to it:", "git switch -c name", ["git branch -d name", "git merge name", "git fetch name"]),
        ("Which HTTP status means 'Not Found'?", "404", ["200", "301", "500"]), ("A primary key must be:", "Unique and non-null", ["Nullable", "Text only", "A foreign key"]),
        ("Unit tests should primarily verify:", "Small isolated units of behavior", ["Only the UI", "Production traffic", "Database backups"]), ("REST resources are commonly identified by:", "URIs", ["CSS selectors", "CPU registers", "File permissions"]),
        ("Which principle says depend on abstractions, not concretions?", "Dependency inversion", ["Single responsibility", "DRY", "YAGNI"]), ("A race condition occurs when:", "Outcome depends on uncontrolled operation timing", ["A query is slow", "Memory is read-only", "A loop is infinite"]),
        ("Breadth-first search uses a:", "Queue", ["Stack", "Priority heap only", "Hash only"]), ("Normalization in databases reduces:", "Data redundancy", ["Network latency", "CPU clock speed", "Encryption"]),
        ("Which is an immutable Python type?", "tuple", ["list", "dict", "set"]), ("An API returning the same result for repeated identical PUT requests is:", "Idempotent", ["Recursive", "Stateful", "Polymorphic"]),
        ("The purpose of a compiler is to:", "Translate source code into another form", ["Design UI", "Store records", "Route packets"]), ("Which traversal visits left, root, right in a BST?", "In-order", ["Pre-order", "Post-order", "Level-order"]),
        ("A foreign key enforces:", "Referential integrity", ["Sorting", "Compression", "Authentication"]), ("Big-O describes:", "Growth rate of resource usage", ["Exact runtime", "Code line count", "CPU brand"]),
    ],
    "web-developer": [
        ("Semantic HTML improves:", "Accessibility and document meaning", ["Database speed", "CPU memory", "DNS routing"]), ("CSS Flexbox is primarily:", "A one-dimensional layout model", ["A database", "A test runner", "An HTTP method"]),
        ("React state updates cause:", "A render reconciliation", ["A server reboot", "A SQL commit", "A DNS lookup"]), ("Which HTTP method is normally safe and read-only?", "GET", ["POST", "PATCH", "DELETE"]),
        ("CORS is enforced mainly by:", "Web browsers", ["SQL servers", "Compilers", "CSS engines"]), ("A 401 response indicates:", "Authentication is required or invalid", ["Resource moved", "Success", "Server timeout"]),
        ("Which attribute connects a label to an input?", "for / htmlFor", ["src", "target", "rel"]), ("Event bubbling travels from:", "Target toward ancestors", ["Window only", "Server to client", "CSS to HTML"]),
        ("localStorage values persist:", "Across browser sessions", ["For one function", "Only until render", "On the server"]), ("A controlled React input gets its value from:", "Component state", ["DNS", "CSS", "The database directly"]),
        ("Which CSS unit is relative to root font size?", "rem", ["px", "vh", "%"]), ("The virtual DOM helps React:", "Compute efficient DOM updates", ["Store passwords", "Compile SQL", "Host images"]),
        ("HTTPS protects data primarily:", "In transit", ["After printing", "In source control", "From all XSS"]), ("Debouncing is useful for:", "Limiting rapid repeated function calls", ["Encrypting cookies", "Joining tables", "Styling grids"]),
        ("A cookie with HttpOnly cannot be read by:", "Client-side JavaScript", ["The server", "The browser", "HTTP requests"]), ("Responsive design adapts to:", "Viewport and device characteristics", ["Database schema", "Git history", "CPU threads"]),
        ("Which hook performs side effects in React?", "useEffect", ["useId only", "useMemo only", "createContext"]), ("A closure retains access to:", "Its lexical scope", ["Only globals", "CSS rules", "HTTP headers only"]),
        ("JSON.parse converts JSON text to:", "A JavaScript value", ["CSS", "HTML", "Binary machine code"]), ("XSS is mitigated by:", "Escaping untrusted output", ["More indexes", "Longer URLs", "Removing TLS"]),
    ],
    "data-analyst": [
        ("The median is resistant to:", "Extreme outliers", ["All missing values", "Duplicate rows", "Sample size"]), ("A LEFT JOIN returns:", "All left rows and matching right rows", ["Only matches", "Only right rows", "No nulls"]),
        ("Standard deviation measures:", "Spread around the mean", ["Causation", "Row count", "Data type"]), ("Which chart best shows a time trend?", "Line chart", ["Pie chart", "Treemap", "Single KPI"]),
        ("GROUP BY is used to:", "Aggregate rows by categories", ["Delete columns", "Encrypt fields", "Sort files"]), ("Correlation proves causation:", "False", ["Always true", "Only for large samples", "Only for charts"]),
        ("A primary key uniquely identifies:", "A table row", ["A database server", "A chart", "A formula"]), ("Missing numeric values may be imputed with median when data is:", "Skewed", ["Encrypted", "Already normalized", "Boolean"]),
        ("A p-value is evaluated against:", "A significance level", ["A file size", "A join key", "A color scale"]), ("Which SQL function counts rows?", "COUNT", ["MEAN", "TOTALROWS", "ROWS"]),
        ("A dashboard KPI should be:", "Tied to a clear business objective", ["Decorative", "Always a pie chart", "Unfiltered"]), ("ETL stands for:", "Extract, Transform, Load", ["Evaluate, Test, Learn", "Enter, Transfer, Link", "Extract, Type, Loop"]),
        ("An inner join keeps:", "Rows matching in both tables", ["Every left row", "Every right row", "No matching rows"]), ("A histogram displays:", "A numeric distribution", ["Source code", "A network", "Text paragraphs"]),
        ("In spreadsheets, $A$1 is:", "An absolute reference", ["A relative reference", "A chart", "An error"]), ("Data validation helps ensure:", "Values follow defined rules", ["Every value is unique", "Files are smaller", "Queries use joins"]),
        ("A confidence interval estimates:", "A plausible range for a population parameter", ["Every raw value", "Database uptime", "A causal effect always"]), ("A dimension table usually stores:", "Descriptive attributes", ["Only transaction amounts", "Application logs only", "Compiled code"]),
        ("Which Python library is widely used for tabular data?", "pandas", ["pytest", "flask", "pygame"]), ("Before analysis, duplicate records should be:", "Investigated against business rules", ["Always ignored", "Always doubled", "Converted to images"]),
    ],
    "cloud-engineer": [
        ("Horizontal scaling means:", "Adding more instances", ["Adding CPU to one instance", "Compressing logs", "Changing regions only"]), ("An availability zone is:", "An isolated location within a cloud region", ["A user account", "A DNS record", "A programming language"]),
        ("Infrastructure as Code enables:", "Repeatable versioned provisioning", ["Manual-only setup", "Faster typing", "No monitoring"]), ("A load balancer distributes:", "Traffic across healthy targets", ["Passwords", "Source branches", "Disk blocks only"]),
        ("Object storage is ideal for:", "Durable unstructured files", ["CPU registers", "In-memory locks", "Running processes"]), ("Least privilege grants:", "Only permissions required", ["Administrator to everyone", "No audit logs", "Public access"]),
        ("A container image is:", "An immutable application package", ["A running VM only", "A DNS zone", "A password vault"]), ("Kubernetes uses a Pod as:", "The smallest deployable unit", ["A billing account", "A region", "A firewall rule"]),
        ("RTO describes:", "Target time to restore service", ["Allowed data loss", "CPU speed", "Request count"]), ("RPO describes:", "Acceptable data-loss window", ["Recovery duration", "Network bandwidth", "Instance price"]),
        ("A private subnet typically lacks:", "A direct route to an internet gateway", ["IP addresses", "Routing", "Security rules"]), ("TLS provides:", "Encryption in transit and endpoint authentication", ["Disk compression", "Autoscaling", "SQL joins"]),
        ("Blue-green deployment uses:", "Two production-like environments", ["One untracked server", "No rollback", "Only local machines"]), ("Metrics, logs, and traces are pillars of:", "Observability", ["Normalization", "Compilation", "Virtualization only"]),
        ("A CDN caches content:", "Closer to users", ["Only in source control", "Inside a CPU", "In a password"]), ("Serverless billing commonly tracks:", "Invocations and execution resources", ["Office seats", "Git commits", "DNS names only"]),
        ("A health check determines whether:", "An instance should receive traffic", ["Code is copyrighted", "Users know SQL", "A bill is paid"]), ("Secrets should be stored in:", "A managed secret store", ["Source code", "Public images", "Client-side HTML"]),
        ("Idempotent provisioning means repeated runs:", "Converge on the same desired state", ["Create endless duplicates", "Always fail", "Delete logs"]), ("Multi-region design mainly improves:", "Resilience to regional failure", ["CSS rendering", "Code indentation", "Local disk speed"]),
    ],
}

CODING = {
    "mern-stack-developer": [
        ("Pair Sum", "Given n, target, then n integers, print indices of the first pair whose values sum to target, or -1. Use zero-based indices.", ["5 9\n2 7 11 1 8\n", "4 20\n1 2 3 4\n", "6 10\n5 5 3 7 2 8\n"], ["0 1", "-1", "0 1"]),
        ("Balanced Brackets", "Read one string containing only ()[]{}. Print YES if brackets are balanced, otherwise NO.", ["([]{})\n", "([)]\n", "{{[[(())]]}}\n", "]\n"], ["YES", "NO", "YES", "NO"]),
    ],
    "web-developer": [
        ("URL Slug", "Read one line. Convert it to a lowercase URL slug: trim it, replace each run of non-alphanumeric characters with one hyphen, and remove edge hyphens.", ["Hello, Campus Hiring!\n", "  React & Django  Portal  \n", "Already-slugged\n"], ["hello-campus-hiring", "react-django-portal", "already-slugged"]),
        ("Unique Visitors", "Read n followed by n visitor IDs. Print the number of distinct IDs, treating IDs as case-sensitive.", ["6\na b a C c b\n", "4\nu1 u2 u3 u4\n", "5\nx x x x x\n"], ["4", "4", "1"]),
    ],
    "data-analyst": [
        ("Clean Average", "Read n then n tokens, each an integer or NA. Print the mean of valid integers rounded to 2 decimal places; print 0.00 if none are valid.", ["5\n10 NA 20 30 NA\n", "3\nNA NA NA\n", "4\n1 2 2 3\n"], ["20.00", "0.00", "2.00"]),
        ("Mode with Tie-break", "Read n then n integers. Print the most frequent value. If tied, print the smallest tied value.", ["7\n4 2 4 3 2 4 2\n", "5\n9 8 7 6 5\n", "6\n1 1 2 2 3 3\n"], ["2", "5", "1"]),
    ],
    "cloud-engineer": [
        ("Healthy Instances", "Read n, then n lines: instance_name status. Print healthy instance names (status UP) sorted lexicographically, one per line; print NONE if empty.", ["4\napi-2 UP\ndb-1 DOWN\napi-1 UP\njob-1 DOWN\n", "2\na DOWN\nb DOWN\n", "3\nz UP\nx UP\ny UP\n"], ["api-1\napi-2", "NONE", "x\ny\nz"]),
        ("Merge Maintenance Windows", "Read n intervals (start end), one per line. Merge overlapping intervals and print each merged interval as 'start end' in ascending order.", ["4\n1 3\n2 6\n8 10\n9 12\n", "3\n1 2\n3 4\n5 6\n", "1\n0 24\n"], ["1 6\n8 12", "1 2\n3 4\n5 6", "0 24"]),
    ],
}


class Command(BaseCommand):
    help = "Seed the fixed aptitude, role MCQ, and coding banks"

    def handle(self, *args, **options):
        Question.objects.all().delete()
        for category, rows in APTITUDE.items():
            for prompt, answers, correct in rows:
                Question.objects.create(round_type="aptitude", category=category, prompt=prompt, options=answers, correct_option=correct)
        rng = random.Random(42)
        for role, rows in TECH.items():
            for prompt, correct, wrong in rows:
                answers = wrong + [correct]
                rng.shuffle(answers)
                Question.objects.create(round_type="technical", category="technical", role=role, prompt=prompt, options=answers, correct_option=answers.index(correct))
        for role, problems in CODING.items():
            for title, description, inputs, outputs in problems:
                tests = [{"input": value, "output": outputs[index]} for index, value in enumerate(inputs)]
                Question.objects.create(
                    round_type="coding", category="coding", role=role,
                    prompt=f"{title}\n\n{description}\n\nWrite a complete program that reads from standard input and writes to standard output.",
                    starter_code={"python": "# Read from standard input and print the answer\n", "javascript": "// Read with fs.readFileSync(0, 'utf8') and print the answer\n"},
                    test_cases=tests, visible_test_count=min(2, len(tests)),
                )
        call_command("seed_specialized_roles")
        self.stdout.write(self.style.SUCCESS(f"Seeded {Question.objects.count()} questions"))
