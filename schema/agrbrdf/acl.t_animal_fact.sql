--
-- Name: t_animal_fact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE t_animal_fact FROM PUBLIC;
REVOKE ALL ON TABLE t_animal_fact FROM agrbrdf;
GRANT ALL ON TABLE t_animal_fact TO agrbrdf;
GRANT SELECT ON TABLE t_animal_fact TO gbs;


