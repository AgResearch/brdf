--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact2
    ADD CONSTRAINT "$1" FOREIGN KEY (genetictestfact) REFERENCES genetictestfact(obid);


