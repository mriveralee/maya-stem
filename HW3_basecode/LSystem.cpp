#include "LSystem.h"
#include <fstream>
#include <stack>
#include "Quaternion.h"

#pragma warning(disable : 4244)
#pragma warning(disable : 4290)
#include "matrix.h"

#define Rad2Deg 57.295779513082320876798154814105
#define Deg2Rad 0.017453292519943295769236907684886

const vec3 UP_AXIS = vec3(0,1,0);
const vec3 LEFT_AXIS = vec3(1,0,0);
const vec3 FORWARD_AXIS = vec3(0,0,1);




LSystem::LSystem() : mDfltAngle(22.5), mDfltStep(1.0) {
	mHasResources = false;
}

void LSystem::setDefaultAngle(float degrees) {
    mDfltAngle = degrees;
}

void LSystem::setDefaultStep(float distance) {
    mDfltStep = distance;
}

float LSystem::getDefaultAngle() const {
    return mDfltAngle;
}

float LSystem::getDefaultStep() const {
    return mDfltStep;
}

const std::string& LSystem::getGrammarString() const {
    return mGrammar;
}

void LSystem::reset() {
    current = "";
    iterations.clear();
    productions.clear();
}

const std::string& LSystem::getIteration(unsigned int n) {
    if (n >= iterations.size()) {
        for (unsigned int i = iterations.size(); i <= n; i++) {
            current = iterate(current);
            iterations.push_back(current);
        }
    }
    return iterations[n];
}

void LSystem::loadProgram(const std::string& fileName) {
    reset();

    std::string line;
    std::ifstream file(fileName.c_str());
    if (file.is_open()) {
        while (file.good()) {
            getline(file,line);
            addProduction(line);
        }
    }
    // for each line in p, add production
    file.close();
}

void LSystem::loadProgramFromString(const std::string& program) {
    reset();
    mGrammar = program;

    size_t index = 0;
    while (index < program.size()) {
        size_t nextIndex = program.find("\n", index);
        std::string line = program.substr(index, nextIndex);
        addProduction(line);
        if (nextIndex == std::string::npos) break;
        index = nextIndex+1;
    }
}

void LSystem::addProduction(std::string line) {
    size_t index;

    // 1. Strip whitespace
    while ((index = line.find(" ")) != std::string::npos) {
        line.replace(index, 1, "");
    }

    if (line.size() == 0) return;

    // 2. Split productions
    index = line.find("->");
    if (index != std::string::npos) {
        std::string symFrom = line.substr(0, index);
        std::string symTo = line.substr(index+2);
        productions[symFrom] = symTo;
    } else { 
		// assume its the start sym
        current = line;
    }
}

std::string LSystem::iterate(const std::string& input) {
    std::string output = "";
    for (unsigned int i = 0; i < input.size(); i++) {
        std::string sym = input.substr(i,1);
        std::string next = productions.count(sym) > 0? productions[sym] : sym;
        output = output + next;
    }
    return output;
    //for each sym in current state, replace the sym
}


LSystem::Turtle::Turtle() :
    pos(0,0,0),
    up(UP_AXIS),
    forward(FORWARD_AXIS),
    left(LEFT_AXIS) {
}

LSystem::Turtle::Turtle(const LSystem::Turtle& t) {
    pos = t.pos;
    up = t.up;
    forward = t.forward;
    left = t.left;
}

LSystem::Turtle& LSystem::Turtle::operator=(const LSystem::Turtle& t) {
    if (&t == this) return *this;

    pos = t.pos;
    up = t.up;
    forward = t.forward;
    left = t.left;
    return *this;
}

void LSystem::Turtle::moveForward(float length) {
    pos = pos + length * forward;
}


void LSystem::Turtle::applyUpRot(float degrees) {
    math::RotationMatrix<float> mat(2,Deg2Rad*degrees); // Z axis
    math::RotationMatrix<float> world2local(forward, left, up);
    up =  world2local * mat * UP_AXIS;
    left = world2local * mat * LEFT_AXIS;
    forward = world2local * mat * FORWARD_AXIS;
}

void LSystem::Turtle::applyLeftRot(float degrees) {
	///std::map<std::string, int mMap = std::map();
    math::RotationMatrix<float> mat(1,Deg2Rad*degrees); // Y axis
    math::RotationMatrix<float> world2local(forward, left, up);
    up =  world2local * mat * UP_AXIS;
    left = world2local * mat * LEFT_AXIS;
    forward = world2local * mat * FORWARD_AXIS;
}

void LSystem::Turtle::applyForwardRot(float degrees) {
    math::RotationMatrix<float> mat(0,Deg2Rad*degrees); // X axis
    math::RotationMatrix<float> world2local(forward, left, up);
    up =  world2local * mat * UP_AXIS;
    left = world2local * mat * LEFT_AXIS;
    forward = world2local * mat * FORWARD_AXIS;
}

void LSystem::process(unsigned int n,
    std::vector<Branch>& branches) {
    std::vector<Geometry> models;
    process(n,branches,models);
}

/**				
 * Processes the LSystem to via Python get branches and flowers
 * flowers:  vector of vector of floats: [posx, posy, poz]
 * branches: vector of vector of floats: [startx, starty, startz, endx, endy, endz]
 **/
void LSystem::processPy(unsigned int n,
	std::vector<std::vector<float> >& branches, std::vector<std::vector<float> >& flowers) {

	std::vector<Branch> preBranches;
    std::vector<Geometry> preFlowers;

	process(n, preBranches, preFlowers);

	// Convert Branches to PyBranches
	for (unsigned int i = 0; i < preBranches.size(); i++) {
		// Get prebranch
		Branch b = preBranches.at(i);

		// Get start & end of branch
		vec3 start = b.first;
		vec3 end = b.second;

		// Make  vector of floats based on start and end points
		vector<float> values = vector<float>();
		values.push_back(start[0]);
		values.push_back(start[1]);
		values.push_back(start[2]);
		values.push_back(end[0]);
		values.push_back(end[1]);
		values.push_back(end[2]);

		// Now push onto branches
		branches.push_back(values);
	}

	// Convert Flowers to PyFlowers
	for (unsigned int i = 0; i < preFlowers.size(); i++) {
		// Get preFlower
		Geometry f = preFlowers.at(i);

		// Get symbol of geometry
		string sym = f.second;

		// If not a flower, do nothing
		if (sym != "*") continue;

		// Get the Flower's coordinate
		vec3 start = f.first;

		// Make vector of floats based on start coordinate of flower
		vector<float> values = vector<float>();
		values.push_back(start[0]);
		values.push_back(start[1]);
		values.push_back(start[2]);

		// Now push onto flowers
		flowers.push_back(values);
	}


}


void LSystem::Turtle::rotateByAxisAngle(const vec3 axis, float angle) {
	Quaternion q = Quaternion::Quaternion();
	q.FromAxisAngle(axis, angle * Deg2Rad); 
	math::RotationMatrix<float> mat = q.toRotationMatrix();
    math::RotationMatrix<float> world2local(forward, left, up);
    //up =  world2local * mat * UP_AXIS;
    //left = world2local * mat * LEFT_AXIS;
    //forward = world2local * mat * FORWARD_AXIS;
	up =  mat * UP_AXIS;
    left = mat * LEFT_AXIS;
    forward = mat * FORWARD_AXIS;
}



// LOOK: This is where the L-System creates the branches and the flowers.
//        Branches are returns in the "branches" vector and flowers (or other symbols) are
//        returned in the "models" vector.
void LSystem::process(unsigned int n,
    std::vector<Branch>& branches,
    std::vector<Geometry>& models) {
    Turtle turtle;
    std::stack<Turtle> stack;

    // Init so we're pointing up
    turtle.applyUpRot(90);

    std::string insn = getIteration(n);

    std::vector<int> depth;
    int curDepth = 0;

	// For updating bud rotations based on light positions in maya
	float budAngle = 0.0;
	vec3 budAxis = vec3();
	float prevDefAngle;
	vec3 initialStart;
	std::string prevSym = "";

    for (unsigned int i = 0; i < insn.size() && i <= 1; i++) {
        std::string sym = insn.substr(i,1);
		initialStart = turtle.pos;



		if (sym == "F" && (prevSym.compare(sym) != 0)) {
            vec3 start = turtle.pos;
            turtle.moveForward(mDfltStep);
            branches.push_back(Branch(start,turtle.pos));
        }
        else if (sym == "f") {
            turtle.moveForward(mDfltStep);
        }
        else if (sym == "+") {
            turtle.applyUpRot(mDfltAngle);
        }
        else if (sym == "-") {
            turtle.applyUpRot(-mDfltAngle);
        }
        else if (sym == "&") {
            turtle.applyLeftRot(mDfltAngle);
        }
        else if (sym == "^") {
            turtle.applyLeftRot(-mDfltAngle);
        }
        else if (sym == "\\") {
            turtle.applyForwardRot(mDfltAngle);
        }
        else if (sym == "/") {
            turtle.applyForwardRot(-mDfltAngle);
        }
        else if (sym == "|") {
            turtle.applyUpRot(180);
        }
        else if (sym == "[") {
            stack.push(turtle);
			//If is a bud, push turtle onto BudStack,
			// find next "]" close bracket, then move i to that position
			// Main branch can keep growing but we want to be able to add 
			// a branch from the bud
			//if (isABud(turtle.pos)) {
			//	Turtle budTurtle = Turtle(turtle);
			//	mBudPosStack.push(budTurtle);
			//	// Do some growth with the bud

			//	int nextPos = insn.find("]", i);
			//	if (nextPos != string::npos) {
			//		i = nextPos;
			//		continue;
			//	}

			//} else {
			//	// Push if not a bud
			//	stack.push(turtle);
			//}
        }
        else if (sym == "]") {
            turtle = stack.top();
            stack.pop();
        }
        else {
			models.push_back(Geometry(turtle.pos, sym));
        }		
		prevSym = sym;
	 }
	// Update the growth for each bud, if necessary
	//for (unsigned int i = 0; i < mBudPositions.size(); i++) {
	//	// Bud Position
	//	std::vector<float> budPos = mBudPositions.at(i);
	//	vec3 bPos = vec3(budPos.at(0), budPos.at(1), budPos.at(2));
	//	
	//	// Optimal Position
	//	std::vector<float> optPos = mBudDirs.at(i);
	//	vec3 oPos = vec3(optPos.at(0), optPos.at(1), optPos.at(2));

	//	// Make branch to the opt positon
	//	branches.push_back(Branch(bPos, oPos));
	//	// turtle.rotateByAxisAngle(budAxis, budAngle);
	//	// prevDefAngle = mDfltAngle;
	//	// Grow towards the Light
	//	//mDfltAngle = budAngle;
	//}
}

/**
 * 	Sets whether this LSystem has Resources to use
 **/ 
void LSystem::setHasResources(bool hasResources) {
	mHasResources = hasResources;
}


/**
 * Sets the optimal growth tuples
 **/
void LSystem::setOptimalBudDirs(
	std::vector<std::vector<float> > buds, 
	std::vector<std::vector<float> > dirs, 
	std::vector<float> angles) {
		// Clear old arrays
		mBudPositions.clear();
		mBudAngles.clear();
		mBudDirs.clear();

		// Set the new Bud Position data
		for (unsigned int i = 0; i < buds.size(); i++) {
			// Get the bud
			std::vector<float> b = buds.at(i);

			// Create new vector for c++ to hold
			std::vector<float> newB = std::vector<float>();

			// Create a new bud vector
			newB.push_back(b.at(0));
			newB.push_back(b.at(1));
			newB.push_back(b.at(2));

			// Push back the bud position
			mBudPositions.push_back(newB);

			// Get the direction
			std::vector<float> d = dirs.at(i);
			
			// Create new vector for c++ to hold
			std::vector<float> newD = std::vector<float>();

			// Create a new dir vector
			newD.push_back(d.at(0));
			newD.push_back(d.at(1));
			newD.push_back(d.at(2));

			// Push back the dir position
			mBudDirs.push_back(newD);

			// Get the bud angle data
			float a = angles.at(i);

			// Add the angle 
			mBudAngles.push_back(a);

		}
}

/**
 * Gets the optimal growth tuples 
 **/ 
void LSystem::getOptimalBudDirs(
	std::vector<std::vector<float> >& buds, std::vector<std::vector<float> >& dirs, std::vector<float>& angles) {
		// Set the new data
		for (unsigned int i = 0; i < mBudPositions.size(); i++) {
			// Get the stored bud
			std::vector<float> b = mBudPositions.at(i);

			// Create new vector for c++ to hold
			std::vector<float> newB = std::vector<float>();

			// Create a new bud vector
			newB.push_back(b.at(0));
			newB.push_back(b.at(1));
			newB.push_back(b.at(2));

			// Push back the bud position
			buds.push_back(newB);

			// Get the stored direction
			std::vector<float> d = mBudDirs.at(i);

			// Create new vector for c++ to hold
			std::vector<float> newD = std::vector<float>();

			// Create a new dir vector
			newD.push_back(d.at(0));
			newD.push_back(d.at(1));
			newD.push_back(d.at(2));

			// Push back the dir vector
			dirs.push_back(newD);

			// Get stored angle
			float a = mBudAngles.at(i);
			// Push back the angle
			angles.push_back(a);
		}
}

/**
 * Returns true if a given position is a bud
 **/
bool LSystem::isABud(vec3 pos) {
	for (unsigned int i = 0; i < mBudPositions.size(); i++) {
		std::vector<float> budPos = mBudPositions.at(i);
		if (budPos[0] == pos[0]
			&& budPos[1] == pos[1]
			&& budPos[2] == pos[2]) {
				return true;
		}
	}
	return false;
}


/**
 * Returns the budAxis and Angle for a given position if it is a bud
 **/
 bool LSystem::getBudAngle(vec3 pos, vec3& budAxis, float &budAngle) {

	for (unsigned int i = 0; i < mBudPositions.size(); i++) {
		std::vector<float> budPos = mBudPositions.at(i);
		if (budPos[0] == pos[0]
			&& budPos[1] == pos[1]
			&& budPos[2] == pos[2]) {
				
				// Get bud dir/axis
				std::vector<float> axis = mBudDirs.at(i);
				budAxis[0] = axis.at(0);
				budAxis[1] = axis.at(1);
				budAxis[2] = axis.at(2);

				// Get angle
				budAngle = mBudAngles.at(i);
				return true;
		}
	}
	return false;
}

/**
 * Updates bud geometry so that is grows towards a light
 **/
void LSystem::updateBudGeometry(unsigned int n, std::vector<std::vector<float> >& branches, std::vector<std::vector<float> >& flowers) {
	// for each bud pos, go through and complete growth towards the light
	// push back onto branches
	// static int MIN_ITERATIONS = 2;
	static int MAX_ITERATIONS = 2;
	Turtle t = Turtle();
	for (unsigned int i = 0; i < mBudPositions.size(); i++) {
		// Get the bud position
		std::vector<float> bp = mBudPositions.at(i);
		vec3 budPos = vec3(bp[0], bp[1], bp[2]); 

		// Get the light Pos
		std::vector<float> lp = mBudDirs.at(i);
		vec3 lightPos = vec3(lp[0], lp[1], lp[2]);
		
		// Set the turtle's position to be where the bud is
		t.pos = budPos;

		// Set the number of iterations
		int numIters = (rand() % MAX_ITERATIONS) + n;


		// Now move the Turtle
		for (unsigned int j = 0; j < numIters; j++) {
			int randMovement = rand() % 5;
			int randAngle = rand() % 45 + 30;
			switch (randMovement) {
				case 0:
					// Move Forward
					t.moveForward(mDfltStep + 0.1f);
					break;
				case 1:
					// Apply Left
					t.applyUpRot(randAngle);
					break;
				case 2:
					// Up Rotation
					t.applyUpRot(-randAngle);
					break;
				case 3:
					t.applyLeftRot(randAngle);
					break;
				case 4:
					t.applyLeftRot(-randAngle);
				default:
					break;
			}
			// Find max growth position toward light 
			// (we don't want all the buds to growth fully to the light)
			// We want it to be between 40-75
			vec3 initialPos = t.pos;
			int growthRate = rand() % 25 + 10;
			vec3 growthVec = growthRate * (lightPos - initialPos);
			
			// Update the turtle position
			t.pos = initialPos + growthVec;

			// Add a new branch 
			std::vector<float> b = std::vector<float>();
			b.push_back(initialPos[0]);
			b.push_back(initialPos[1]);
			b.push_back(initialPos[2]);
			b.push_back(t.pos[0]);
			b.push_back(t.pos[1]);
			b.push_back(t.pos[2]);
			// Add it to the branches!
			branches.push_back(b);
		}
		// Make a Turtle w/ Bud Position
		// USe Grammar String (1 iteration) to move position
		// Loop for numTimes
		// Make growth towards light (defaultStepSize << rand << distToLight
		// Rotate and growth away
	}
}
