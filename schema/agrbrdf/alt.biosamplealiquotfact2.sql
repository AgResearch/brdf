--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact2
    ADD CONSTRAINT "$1" FOREIGN KEY (biosamplealiquotfact) REFERENCES biosamplealiquotfact(obid);


