
import pandas as pd
import flopy

def disu2disv(filename, workspace=None):
    def get_sentences(filename, keyword):
        with open(filename, 'r') as f:
            begin = 'BEGIN '+keyword
            end = 'END '+keyword
            results = []
            start = False
            for line in f:
                if begin in line:
                    start = True  # results = []
                elif end in line:
                    start = False  # yield results
                if start:  # else:
                    results.append(line)
            results = [i.strip().split() for i in results[2:]]
            df = pd.DataFrame(results, dtype='float')

            # .astype('str')#.replace('-1',np.nan)
            df2 = (df-1).fillna(-1e30).astype('int')
            df2[[1, 2]] = df[[1, 2]]
            if keyword == 'CELL2D':
                df2[3] = df[3].astype('int')
            # retains the data type
            new_li = list(map(list, df2.itertuples(index=False)))

            new_li2 = [[e for e in l if e > -99999] for l in new_li]
            return new_li2

    cell2d = get_sentences(filename, 'CELL2D')
    ncpl = len(cell2d)
    vertices = get_sentences(filename, 'VERTICES')

    # reorder vertices in cell2d clockwise
    nvert = len(vertices)
    for cell in range(ncpl):
        #cell = 14298
        vlist = cell2d[cell][4:]
        vtemp = []
        for v in vlist:
            if v == None:
                continue
            vtemp.append(list(vertices[v]))

        area = 0
        edge = 0
        for i in range(len(vtemp)):
            v = vtemp[i]
            x1 = v[1]
            y1 = v[2]
            if v == vtemp[-1]:
                x2 = vtemp[0][1]
                y2 = vtemp[0][2]
            else:
                x2 = vtemp[i+1][1]
                y2 = vtemp[i+1][2]
            area += (x1 * y2 - x2 * y1)
            edge += (x2-x1)*(y2+y1)

        if area > 0:  # negative area means clockwise; 
            cell2d[cell] = [i for i in cell2d[cell] if i != None]
            cell2d[cell][4:] = cell2d[cell][4:][::-1]

    def get_areas(workspace):
        sim = flopy.mf6.MFSimulation.load(sim_ws=workspace, verbosity_level=0)
        m = sim.get_model(list(sim.model_names)[0])
        area = m.dis.area
        return area

    area = get_areas(workspace)
    
    return nvert, vertices, cell2d, ncpl, area
