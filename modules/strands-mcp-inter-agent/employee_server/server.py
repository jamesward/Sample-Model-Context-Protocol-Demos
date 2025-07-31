from employee_data import SKILLS, EMPLOYEES

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("employee-server", stateless_http=True, host="0.0.0.0", port=8002)

@mcp.tool()
def get_skills() -> set[str]:
    """all of the skills that employees may have - use this list to figure out related skills"""
    print("get_skills")
    return SKILLS

@mcp.tool()
def get_employees_with_skill(skill: str) -> list[dict]:
    """employees that have a specified skill - output includes fullname (First Last) and their skills"""
    print(f"get_employees_with_skill({skill})")
    skill_lower = skill.lower()
    return [employee for employee in EMPLOYEES if any(s.lower() == skill_lower for s in employee["skills"])]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
